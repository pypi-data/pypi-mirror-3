# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name='django-stdimage',
    version='0.2.2',
    description='Django Standarized Image Field',
    author='garcia.marc',
    author_email='garcia.marc@gmail.com',
    url='https://github.com/humanfromearth/django-stdimage',
    license='lgpl',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
    packages=['stdimage'],
    requires=['django (>=1.0)',],
)
