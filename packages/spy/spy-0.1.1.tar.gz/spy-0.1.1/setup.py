#!/usr/bin/env python
from distutils.core import setup


setup(
    name='spy',
    description='Super simple monitoring for long running jobs',
    author='George Courtsunis',
    author_email='gjcourt@gmail.com',
    url='http://github.com/gjcourt/spy',
    version='0.1.1',
    packages=['spy', 'spy.server'],
    requires=['Flask (==0.8)']
    )

