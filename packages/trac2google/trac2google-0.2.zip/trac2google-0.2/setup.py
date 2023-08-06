#!/usr/bin/python
from setuptools import setup, find_packages

setup(
    name='trac2google',
    version='0.2',
    description='Create events on google calendar based on trac entries',
    long_description = open("README.txt").read(),
    author='Tiberiu ichim',
    author_email='tibi@pixelblaster.ro',
    license='GPLv3',
    url='',
    packages=find_packages(),
    install_requires = [
        'lxml',
        'pytz',

        #'gdata',
        #'icalendar',
        #'google-calendar-helper',
        #'iso8601'
    ],
    entry_points={
        "console_scripts":[
            "trac2google = trac2google.calendar:main" ,
            ],
        },

)
