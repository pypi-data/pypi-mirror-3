#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages
import os

version = __import__('django_ulogin').get_version()
readme = os.path.join(os.path.dirname(__file__), 'README.rst')

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Framework :: Django'
]

setup(
    name='django-ulogin',
    author='Mikhail Porokhovnichenko <marazmiki@gmail.com>',
    version=version,
    author_email='marazmiki@gmail.com',
    url='http://pypi.python.org/pypi/django-ulogin',
    download_url='http://bitbucket.org/marazmiki/django-ulogin/get/tip.zip',
    description='User social authentication with ulogin.ru service',
    long_description=open(readme).read(),
    license='MIT license',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'Django>=1.3.1',
        'requests>=0.7.4',
        'mock>=0.8.0',
    ],
    packages=find_packages(exclude=['test_project', 'test_project.*']),
    include_package_data=True,
    zip_safe=False)
