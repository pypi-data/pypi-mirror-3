#! /usr/bin/env python

try:
    from distutils2.core import setup
except:
    from distutils.core import setup

setup(name = 'avalanche',
      description = 'Web Framework with a focus on testability and reusability',
      version = '0.2.0',
      license = 'MIT',
      author = 'Eduardo Naufel Schettino',
      author_email = 'schettino72@gmail.com',
      url = 'http://packages.python.org/avalanche/overview.html',
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      packages = ['avalanche'],
      install_requires = ['jinja2'],
      long_description = open('doc/overview.rst').read(),
      )

