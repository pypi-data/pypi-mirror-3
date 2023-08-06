#!/usr/bin/env python
# coding: utf-8

from setuptools import setup


setup(
    name='json_tools',
    version='0.1.27',

    packages=['json_tools'],
    package_dir={'json_tools': 'lib'},
    install_requires=['colorama'],

    entry_points={
        'console_scripts': [
            'json = json_tools.__main__:main',
        ]
    },

    author='Vadim Semenov',
    author_email='protoss.player@gmail.com',
    url='',

    description='A set of tools to manipulate JSON: diff, patch, pretty-printing',
    classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
    ],
)
