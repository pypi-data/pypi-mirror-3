'''
Simple, reusable flask blueprint that you can mount in your app to get a basic purchase flow for a single item.
'''

from setuptools import setup

setup(
    name='flask-itemshop',
    version='0.1',
    url='http://lost-theory.org/',
    license='BSD',
    author='Steven Kryskalla',
    author_email='skryskalla@gmail.com',
    description=__doc__,
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