#-*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='python-nagios-frontend',
    version='0.6.1',
    description='A nagios frontend, which makes things looks nicer. Provides HTML, JSON and XML. Based on the excellent package "balbec".',
    author='Magnus Kulke, Kristian Oellegaard, Ales Kocjancic',
    author_email='kristian@oellegaard.com',
    url='https://github.com/KristianOellegaard/python-nagios-frontend',
    packages=find_packages(),
    license = "AGPL",
    install_requires=[
        'lxml',
        'twisted>=0.11',
        'simplejson',
    ],
    entry_points={
        'console_scripts': [
            'python-nagios-frontend = balbec.balbec_twisted:main',
        ]
    },
)