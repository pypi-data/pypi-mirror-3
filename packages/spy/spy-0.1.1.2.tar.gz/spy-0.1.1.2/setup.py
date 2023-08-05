#!/usr/bin/env python
from distutils.core import setup

templates = 'something'

setup(
    name='spy',
    description='Super simple monitoring for long running jobs',
    author='George Courtsunis',
    author_email='gjcourt@gmail.com',
    url='http://github.com/gjcourt/spy',
    version='0.1.1.2',
    packages=['spy', 'spy.server', 'spy.server.templates'],
    data_files=[
        # ('spy/server/templates', ['spy/server/templates/monitor.html']),
        ('/tmp', ['spy/server/templates/monitor.html']),
    ],
    requires=['Flask (==0.8)']
    )

