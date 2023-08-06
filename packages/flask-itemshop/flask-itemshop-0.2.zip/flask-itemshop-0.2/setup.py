'''
Simple flask blueprint (``ItemBP``) that you can mount in your app to get
a basic purchase flow for a single item. Credit card processing is done with
``stripe.js`` and the stripe python API.

See the **documentation** for more information:

* http://packages.python.org/flask-itemshop/

There is a **demo site** online here:

* http://itemshopdemo.lost-theory.org/
'''

SHORT_DESC = '''
Simple flask blueprint (ItemBP) that you can mount in your app to get a basic purchase flow for a single item. Credit card processing is done with stripe.js and the stripe python API.
'''

from setuptools import setup

setup(
    name='flask-itemshop',
    version='0.2',
    url='https://bitbucket.org/lost_theory/flask-stripe-blueprint/',
    license='BSD',
    author='Steven Kryskalla',
    author_email='skryskalla@gmail.com',
    description=SHORT_DESC,
    long_description=__doc__,
    packages=['itemshop'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'stripe>=1.6.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Office/Business',
    ],
)