# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='django-orderable-inlines',
    version='0.0.2',
    description='Drag-to-reorder inline model admins for Django',
    long_description=readme,
    author='Elijah Rutschman',
    author_email='elijahr+django-orderable-inlines@gmail.com',
    url='https://github.com/elijahr/django-orderable-inlines',
    license=license,
    packages=find_packages(exclude=('tests',)),
    package_data={ 'orderable_inlines': ['static/*'], },
)
