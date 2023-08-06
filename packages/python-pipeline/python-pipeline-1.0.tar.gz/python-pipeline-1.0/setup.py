'''
*python-pipeline* lets you create pipelines of iterators.

.. note:: This is transitional package for grapevine_.

.. _grapevine: http://jwilk.net/software/python-grapevine
'''

import distutils.core

classifiers = '''
Development Status :: 7 - Inactive
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 2
Topic :: Software Development :: Libraries :: Python Modules
'''.strip().splitlines()

distutils.core.setup(
    name = 'python-pipeline',
    version = '1.0',
    license = 'MIT',
    platforms = ['any'],
    requires = ['grapevine'],
    description = 'iterator pipelines',
    long_description = __doc__.strip(),
    classifiers = classifiers,
    author = 'Jakub Wilk',
    author_email = 'jwilk@jwilk.net',
    py_modules = ['pipeline']
)

# vim:ts=4 sw=4 et
