# -*- coding: utf-8 -*-
"""
"""
from distutils.core import setup

setup(
    name = 'gameserver',
    version = '0.1.0',
    license = 'Apache Software License',
    url = 'http://gameserverapp.appspot.com',
    description = "gameserver implements a rest transactional game server.",
    long_description = __doc__,
    author = 'Nelson Melo',
    author_email = 'nmelo.cu@gmail.com',
    zip_safe = False,
    platforms = 'any',
    py_modules = [
        'gameserver',
    ],
    packages = [
        'gameserver'
    ],
    include_package_data=True,
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
    ]
)
