from setuptools import setup, find_packages

setup(
    name         = 'getent',
    version      = '0.1',
    author       = 'Wijnand Modderman-Lenstra',
    author_email = 'maze@pyth0n.org',
    description  = 'Python interface to the POSIX getent family of commands',
    long_description = '''
========
 getent
========

Python interface to the POSIX getent family of commands (getpwent, getgrent, getnetent, etc.)


Usage
=====

Here a few examples.

Load the interface::

    >>> import getent

Doing a passwd lookup::

    >>> print dict(getent.passwd('root'))
    {'dir': '/root',
     'gecos': 'root',
     'gid': 0,
     'name': 'root',
     'password': 'x',
     'shell': '/bin/bash',
     'uid': 0}

Doing a group lookup::

    >>> print dict(getent.group('root'))
    {'gid': 0, 'members': [], 'name': 'root', 'password': 'x'}
''',
    license      = 'MIT',
    keywords     = 'getent group passwd shadow network alias host',
    packages     = ['getent'],
)

