#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'emclpy'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ldap_target_ctl',
    version='1.0.0',
    description="Python package to automate the creation of LDAP generic services in Oracle Enterprise Manager",
    long_description=readme + '\n\n' + history,
    author="Tom Lester",
    author_email='tom.lester@oracle.com',
    url='https://dev-git-otes.taleo.net/gitlab/incubator/oem/tree/master/utilities/ldap_target_ctl',
    packages=[
        'ldap_target_ctl',
    ],
    package_dir={'ldap_target_ctl':
                 'ldap_target_ctl'},
    package_data={
        'ldap_target_ctl': ['ldap_target_ctl.conf'],
    },
    include_package_data=True,
    entry_points={'console_scripts': [
        'ldap_target_ctl=ldap_target_ctl:main',
        ],
    },
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='ldap_target_ctl, oem, oracle, em12c',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
