# -*- coding: utf-8 -*-
"""
This module contains the core functionality for implementing a personnel directory within Plone.
"""
import os
import sys
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

name = 'fsd.core'
version = '1.0a1'

install_requires = [
    'setuptools',
    'Plone >=4.1',
    'plone.app.dexterity',
    'z3c.relationfield',
    'plone.formwidget.contenttree',
    'plone.app.registry',
    'plone.app.referenceablebehavior',
    ]
test_requires = [
    'plone.app.testing',
    'z3c.form[test]'
    ]
if sys.version_info < (2, 7,):
    test_requires.append('unittest2')
extras_require = {'test': test_requires}

long_description = '\n\n'.join([read('README.txt'), read('CHANGES.txt')])

DEV_STATES = [
    "Development Status :: 3 - Alpha",
    "Development Status :: 4 - Beta",
    "Development Status :: 5 - Production/Stable",
]
if version.find('a') >= 0:
    state = 0
elif version.find('b') >= 0:
    state = 1
else:
    state = 2
development_status = DEV_STATES[state]

setup(
    name=name,
    version=version,
    author='WebLion Group, Penn State University',
    author_email='support@weblion.psu.edu',
    description="",
    long_description=long_description,
    classifiers=["Framework :: Plone",
                 "Programming Language :: Python",
                 "Intended Audience :: Developers",
                 development_status,
                 ],
    keywords='weblion',
    license='GPL',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
    entry_points="""
# -*- Entry points: -*-
[z3c.autoinclude.plugin]
target = plone
""",
    )
