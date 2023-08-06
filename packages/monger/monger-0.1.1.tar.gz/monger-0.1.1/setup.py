# -*- coding: utf-8 -*-
"""
monger
~~~~

runs mongodump and sends the tarball to S3

"""

from setuptools import setup

setup(
    name='monger',
    version='0.1.1',
    url='https://github.com/aquaya/monger',
    license='MIT',
    author='Matt Ball',
    author_email='matt@aquaya.org',
    description='mongodump to S3',
    long_description=__doc__,
    py_modules=['monger'],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'boto>=2.5.2',
        'envoy>=0.0.2'
    ],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
