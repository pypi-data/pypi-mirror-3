#!/usr/bin/env python

from setuptools import setup, find_packages
import digested

setup(
    name='django-digested',
    description=('Allows you to set up notification emails for your users,'
                 ' sent out either immediately or in regular batches'),
    long_description=open('README').read(),
    packages=['digested',],
    license='See LICENSE file',
    author='Jerome Baum',
    author_email='jerome@jeromebaum.com',
    url='http://unpublished.test',
    include_package_data=True,
    package_data={'digested': ['migrations/*.py']},
    zip_safe=False,
    version=digested.__version__,
)
