# -*- coding: utf-8 -*-
import os
import time
import codecs
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup, find_packages

version = '0.4'

folder = os.path.dirname(os.path.abspath(__file__))

if not os.path.exists(os.path.join(folder, 'PKG-INFO')):
    info = {
        'version': repr(version),
        'timestamp': int(time.time()),
    }
    fd = codecs.open(os.path.join(folder, 'nosango', '__version__.py'), 'w', 'utf-8')
    fd.write("""#-*- coding: utf-8 -*-
version   = %(version)s
timestamp = %(timestamp)s
""" % info)

setup(
    name = 'nosango',
    version = version,
    description = 'A Django test plug-in for Nose.',
    url = 'http://code.google.com/p/nosango/',
    download_url = 'http://pypi.python.org/pypi/nosango/',
    license = 'GNU AGPLv3',
    author = 'ShiningPanda',
    author_email = 'dev@shiningpanda.com',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Testing',
    ],
    install_requires = [
        'Django >= 1.2.3',
    ],
    setup_requires = [
        'nose >= 1.1.2',
    ],
    entry_points = {
        'nose.plugins.0.10': [
            'nosango = nosango.plugin:Nosango'
        ],
    },
    test_suite = 'nose.collector',
)
