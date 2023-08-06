#!/usr/bin/env python
from distutils.core import setup

readme = open('README.txt').read()

conf = dict(
    name='bolg',
    version='0.1.0',
    author='Niels Serup',
    author_email='ns@metanohi.org',
    package_dir={'': '.'},
    py_modules=['bolg'],
    scripts=['bolg'],
    url='http://metanohi.org/projects/bolg/',
    license='COPYING.txt',
    description='',
    classifiers=['Development Status :: 3 - Alpha',
                 'Environment :: Console',
                 'Intended Audience :: Developers',
                 'License :: DFSG approved',
                 'License :: OSI Approved :: Apache Software License',
                 'Topic :: Utilities',
                 'Topic :: Software Development :: Libraries :: Python Modules',
                 'Topic :: Text Processing',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3'
                 ]
)

try:
    # setup.py register wants unicode data..
    conf['long_description'] = readme.decode('utf-8')
    setup(**conf)
except Exception:
    # ..but setup.py sdist upload wants byte data
    conf['long_description'] = readme
    setup(**conf)
