### -*- coding: utf-8 -*- #############################################
# Разработано компанией Стерх (http://sterch.net/)
# Все права защищены, 2008
#
# Developed by Sterch (http://sterch.net/)
# All right reserved, 2008
#######################################################################

"""setup script class for the ZTK-based sterch.scraper package

"""
__author__  = "Polscha Maxim (maxp@sterch.net)"
__license__ = "ZPL"

import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

def alltests():
    import logging
    import pkg_resources
    import unittest

    class NullHandler(logging.Handler):
        level = 50
        
        def emit(self, record):
            pass

    logging.getLogger().addHandler(NullHandler())

    suite = unittest.TestSuite()
    base = pkg_resources.working_set.find(
        pkg_resources.Requirement.parse('sterch.fields.ip')).location
    for dirpath, dirnames, filenames in os.walk(base):
        if os.path.basename(dirpath) == 'tests':
            for filename in filenames:
                if filename.endswith('.py') and filename.startswith('test'):
                    mod = __import__(
                        _modname(dirpath, base, os.path.splitext(filename)[0]),
                        {}, {}, ['*'])
                    suite.addTest(mod.test_suite())
        elif 'tests.py' in filenames:
            continue
            mod = __import__(_modname(dirpath, base, 'tests'), {}, {}, ['*'])
            suite.addTest(mod.test_suite())
    return suite

setup( name='sterch.fields.ip',
    version='0.1.1a',
    url='http://pypi.sterch.net/sterch.fields.ip',
    license='ZPL 2.1',
    description='Provides fields to store IP address and network',
    author='Maksym Polscha',
    author_email='maxp@sterch.net',
    long_description=(
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],

    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['sterch', 'sterch.fields',],
    include_package_data=True,
    install_requires=['setuptools',
                        'zope.interface',
                        'zope.schema',
                        ],
    extras_require={'test': ['zope.testing'],},                        
    test_suite='__main__.alltests',
    tests_require=['zope.testing',],
    )
