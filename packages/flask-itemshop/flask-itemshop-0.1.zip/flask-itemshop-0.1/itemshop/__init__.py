'''
Simple, reusable flask blueprint (``ItemBP``) that you can mount in your app to
get a basic purchase flow for a single item.

Credit card processing is done with stripe.js and the stripe python API.
'''

from flask import Flask, render_template, request, Blueprint, current_app
import stripe

app = Flask(__name__)

#XXX: api_key can either be set globally or per-item using pmt_default_args
#stripe.api_key = 'UwK0UE4tdPGNJckqfiu5UbzUJxHClRjW'

## meta #######################################################################

from functools import wraps

class BlueprintWrapperMeta(type):
    '''
    Collects all the methods that have been decorated with :func:`bp_route`.
    The route arguments are stored in a dictionary ``self._routes`` as ``method_name ->
    (rule, options)``.
    '''
    def __new__(cls, name, bases, attrs):
        attrs['_routes'] = {}
        for (attr_name, attr) in attrs.items():
            if hasattr(attr, "route_rule") and hasattr(attr, "route_options"):
                attrs['_routes'][attr_name] = (attr.route_rule, attr.route_options)
        return super(BlueprintWrapperMeta, cls).__new__(cls, name, bases, attrs)

class BlueprintWrapper(object):
    '''
    Inherit from this class to automatically collect all your routes that have
    been decorated with :func:`bp_route`.
    '''
    __metaclass__ = BlueprintWrapperMeta

def bp_route(rule, **options):
    '''
    Used with ``BlueprintWrapperMeta`` to register routes.

    Decorates the view method with ``route_rule`` and ``route_options``
    attributes that can then be used to instantiate Flask URL rules.
    '''
    def entangle(f):
        @wraps(f)
        def inner(*a, **kw):
            return f(*a, **kw)
        inner.route_rule = rule
        inner.route_options = options
        return inner
    return entangle

## blueprints #################################################################

class ItemBP(BlueprintWrapper):
    '''
    :class:`BlueprintWrapper` that models a shop item. There are two view methods:
    ``index``, to show the form, and ``process``, to process the incoming
    ``stripe_key`` and show the thank you page. There are also two hooks:
    ``pre_purchase`` and ``post_purchase``, that can be overridden to add
    behavior before and after the purchase is made.

    :param name: unique name / ID for the item, used to build the URL rules
        and to search for custom templates
    :param pmt_class: should be a ``stripe.Charge`` or ``stripe.Customer`` class
        or subclass
    :param pmt_class_args: a dict that contains any default values you want to use
        when instatiating ``pmt_class`` (e.g. the price); you could also leave it
        empty and set the arguments by overriding :meth:`pre_purchase`. See the `stripe documentation`_
        for what arguments you can use.

    .. _stripe documentation: https://stripe.com/docs/api?lang=python
    '''

    def __init__(self, name, pmt_class, pmt_default_args=None):
        self.name = name

        #stripe payment class
        assert isinstance(pmt_default_args.get('amount', 0), int), 'amount must be an integer, in cents'
        assert hasattr(pmt_class, 'create'), "pmt_class must have 'create' method like " \
            "stripe.Customer or stripe.Charge"
        self.pmt_class = pmt_class
        self.pmt_default_args = pmt_default_args or {}

        #inner blueprint object
        bp = Blueprint('itemshop.%s' % name, __name__)
        for (name, (rule, options)) in self._routes.items():
            bp.add_url_rule(rule, name, getattr(self, name), **options)
        self._blueprint = bp

    @bp_route('/')
    def index(self):
        '''
        View method. Renders the item page with the credit card form.
        '''
        return render_template(self.get_template('index'),
            item=self
        )

    @bp_route('/process', methods=["POST"])
    def process(self):
        '''     
        View method. Processes incoming ``stripe_key`` (obtained by the client
        with ``stripe.js``) to actually charge the user's credit card.

        You can change / add behavior to this method by overriding
        ``pre_purchase(args)`` and ``post_purchase(args, purchase)``. 
        '''
        args = self.pmt_default_args.copy()
        args['card'] = request.values['stripe_key']

        #which field do we use for email?
        email = request.values['email']
        if issubclass(self.pmt_class, stripe.Charge):
            #Charge uses the "description" field for email address
            args['description'] = email
        elif issubclass(self.pmt_class, stripe.Customer):
            #Customer has an actual "email" field
            args['email'] = email

        #pre_purchase, create charge (stripe API call), then post_purchase
        args = self.pre_purchase(args)
        purchase = self.pmt_class.create(**args)
        template_vars = self.post_purchase(args, purchase) or {}

        #render thanks template
        return render_template(self.get_template('process'),
            item=self,
            purchase=purchase,
            **template_vars
        )

    def get_template(self, name):
        '''
        Locate the custom item template, or fall back to the default template. Templates
        are kept in the ``itemshop`` directory inside your app's template directory. The
        default templates are ``default_index.html`` and ``default_process.html``. To
        use a custom template use the item's name in the filename instead of "``default``".

        You can override this method to change how templates are looked up.
        '''
        templates = (
            "itemshop/%s_%s.html" % (self.name, name),
            "itemshop/default_%s.html" % (name),
        )
        return current_app.jinja_env.get_or_select_template(templates)
        #XXX: just use "return templates" when "template_name_or_list" makes it into a flask release
        #return templates

    def pre_purchase(self, args):
        '''
        Override this to validate form data / purchase arguments, record
        purchase attempts before the Stripe API call is made, modify
        the purchase arguments, etc.

        You can modify the purchase arguments by returning a new dictionary.
        If you don't want to modify the purchase args, just return the same
        ``args`` object that was passed in.

        This method has access to the ``request`` object.
        '''
        return args

    def post_purchase(self, args, purchase):
        '''
        Override this to save completed purchases to a database, send email
        receipts, etc.

        You can also return a dictionary whose values will be sent to the
        ``render_template`` call that displays the 'thanks' page.

        This method has access to the ``request`` object.
        '''
        return {}

    @property
    def price(self):
        '''
        Format ``self.pmt_default_args['amount']`` as a string ``"XX.YY"``,
        if it exists. Otherwise returns an empty string.
        '''
        if self.pmt_default_args.get('amount') is None:
            return ""
        amt = str(self.pmt_default_args.get('amount'))
        cents = int(amt[-2:] or '0')
        dollars = int(amt[:-2] or '0')
        return "%d.%02d" % (dollars, cents)