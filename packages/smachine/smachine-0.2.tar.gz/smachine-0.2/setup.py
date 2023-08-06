#!/usr/bin/env python
from setuptools import setup, find_packages

import smachine

METADATA = dict(
    name='smachine',
    version=smachine.__version__,
    author='Alen Mujezinovic',
    author_email='alen@caffeinehit.com',
    description='Simple finite state machine.',
    url='https://github.com/caffeinehit/smachine',
    keywords='finite state machine fsm',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Web Environment',
        'Environment :: Other Environment',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    test_suite='smachine.tests',
)

if __name__ == '__main__':
    setup(**METADATA)
