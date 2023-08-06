#!/usr/bin/env python

from setuptools import setup

if __name__ == '__main__':
    setup(
          name = 'pyassert',
          version = '0.1.1',
          description = 'Rich assertions library for Python',
          long_description = '''
pyassert is an assertion library for the Python programming language. pyassert aims to provide assertions with provide

* rich functionality: common assertions should be expressed easily
* good readability: assertions should be easy to read and easy to understand to enhance the overall understandability of the test
* independent of the test framework: pyassert assertions work with every Python test environment.
''',
          author = "Alexander Metzner",
          author_email = "halimath.wilanthaou@gmail.com",
          license = 'Apache Software License',
          url = 'https://github.com/halimath/pyassert',
          scripts = [],
          packages = ['pyassert'],
          classifiers = ['Development Status :: 4 - Beta', 'Environment :: Other Environment', 'Intended Audience :: Developers', 'License :: OSI Approved :: Apache Software License', 'Programming Language :: Python', 'Topic :: Software Development :: Quality Assurance', 'Topic :: Software Development :: Testing'],
          
          
          
          zip_safe=True
    )
