#! /usr/bin/env python

try:
    from distutils2.core import setup
except:
    from distutils.core import setup

setup(name = 'avalanche',
      description = 'Web Framework with a focus on testability and reusability',
      version = '0.1.1',
      license = 'MIT',
      author = 'Eduardo Naufel Schettino',
      author_email = 'schettino72@gmail.com',
      py_modules = ['avalanche'],
      url = 'http://packages.python.org/avalanche/overview.html',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      install_requires = ['webapp2', 'jinja2'],
      long_description = open('doc/overview.rst').read(),
      )

