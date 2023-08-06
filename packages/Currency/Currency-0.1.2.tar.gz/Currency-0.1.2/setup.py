#!/usr/bin/env python
from setuptools import setup

setup(
    name='Currency',
    version='0.1.2',
    description='Currency conversion using openexangerates API',
    download_url='https://bitbucket.org/alquimista/currency/downloads',
    #long_description=open('README.md').read(),
    author='Roberto Gea',
    author_email='rogeaa.cyc@gmail.com',
    license='MIT',
    test_suite='unittest_currency',
    py_modules = ('currency',),
    zip_safe=False,
    keywords = 'currency open exange rates',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        ],
    )
