"""
flask-jade2underscore
===============

A small Flask extension that makes it easy to use Jade to Underscore templates compiler (used in Backbone) with your Flask application.

Usage
-----

You can activate it by calling the ``jade2underscore`` function with your Flask app as a parameter:

      from flaskext.jade2underscore import jade2underscore
      jade2underscore(app, underscore_folder='underscore', jade_folder='src/jade')

This will intercept the request to ``underscore_folder`` and compile de file if is necesary using the files from ``jade_folder``.

When you deploy your app you might not want to accept the overhead of checking the modification time of your ``.jade`` and ``.tpl`` files on each request. A simple way to avoid this is wrapping the jade2underscore call in an if statement:

      if app.debug:
          from flaskext.jade2underscore import jade2underscore
          jade2underscore(app)
          
If you do this you'll be responsible for rendering the ``.jade`` files into ``.tpl`` when you deploy in non-debug mode to your production server.


- documentation_
- development_


.. _documentation: https://github.com/weapp/flask-jade2underscore
.. _development: https://github.com/weapp/flask-jade2underscore

"""

from setuptools import setup


setup(
    name='flask-jade2underscore',
    version='0.1',
    url='https://github.com/weapp/flask-jade2underscore',
    license='MIT',
    author='Manuel Albarran',
    #author_email='',
    description='A small Flask extension adds suppot to Jade2Underscore templates compiler (used in Backbone) to Flask.',
    long_description=__doc__,
    packages=['flaskext'],
    namespace_packages=['flaskext'],
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask',
        'PyJade'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
