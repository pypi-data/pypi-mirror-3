# -*- coding: utf-8 -*-
#quckstarted Options:
#
# sqlalchemy: True
# auth:       None
# mako:       True
#
#

import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

testpkgs=['WebTest >= 1.2.3',
               'nose',
               'coverage',
               'wsgiref',
               'repoze.who-testutil >= 1.0.1',
               ]
install_requires=[
    "TurboGears2 >= 2.1.4",
    "PasteDeploy",
    "Mako",
    "zope.sqlalchemy >= 0.4",
    "repoze.tm2 >= 1.0a5",
    "sqlalchemy",
    "sqlalchemy-migrate",
    "tw2.d3>=0.0.5",
    "fedmsg>=0.1.6",
    "moksha>=0.7.0a1",
    "tg.devtools",
    "Pylons==1.0",
    "WebOb<=1.1.1",
    ]

if sys.version_info[:2] == (2,4):
    testpkgs.extend(['hashlib', 'pysqlite'])
    install_requires.extend(['hashlib', 'pysqlite'])

setup(
    name='busmon',
    version='0.2.2',
    description='A webapp for visualizing activity on the Fedora Message Bus.',
    author='Ralph Bean',
    author_email='rbean@redhat.com',
    url='http://github.com/ralphbean/busmon',
    license='GPLv2+',
    setup_requires=["PasteScript >= 1.7"],
    paster_plugins=['PasteScript', 'Pylons', 'TurboGears2', 'tg.devtools'],
    packages=find_packages(exclude=['ez_setup']),
    install_requires=install_requires,
    include_package_data=True,
    test_suite='nose.collector',
    tests_require=testpkgs,
    package_data={'busmon': ['i18n/*/LC_MESSAGES/*.mo',
                                 'templates/*/*',
                                 'public/*/*']},
    message_extractors={'busmon': [
            ('**.py', 'python', None),
            ('templates/**.mako', 'mako', None),
            ('public/**', 'ignore', None)]},

    entry_points={
        'paste.app_factory': (
            'main = busmon.config.middleware:make_app',
        ),
        'paste.app_install': (
            'main = pylons.util:PylonsInstaller',
        ),
        'moksha.consumer': (
            'colorizer = busmon.consumers:MessageColorizer',
        ),
        'moksha.widget': (
            'topics_bar = busmon.widgets:TopicsBarChart',
            'messages_series = busmon.widgets:MessagesTimeSeries',
            'colorized_msgs = busmon.widgets:ColorizedMessagesWidget',
        ),
    },
    dependency_links=[
        "http://www.turbogears.org/2.1/downloads/current/"
        ],
    zip_safe=False
)
