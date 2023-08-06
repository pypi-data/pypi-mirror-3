#!/usr/bin/env python

# Copyright, 2012 AOL Inc.

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    raise SystemExit('We require setuptools. Sorry! Install it and try again: http://pypi.python.org/pypi/setuptools')
import os
import sys

# Get version from pkg index
from hammer import __version__

# Names of required packages
requires = [
    #'trigger',
]

class CleanCommand(Command):
    user_options = []
    def initialize_options(self):
        self.cwd = None
    def finalize_options(self):
        self.cwd = os.getcwd()
    def run(self):
        os.system ('rm -rf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


desc = 'Hammer is a framework for managing load-balancer configuration'
long_desc = '''
This is a stub for the Hammer project.

Hammer is used to centrally manage, track and maintain load-balanacer
configurations. It will support A10, NetScalers, and more and will store all
configuration data in a vendor-agnostic form so that they may be easily
portable. 
'''

setup(
    name='hammer',
    version=__version__,
    author='Jathan McCollum',
    author_email='jathan@gmail.com',
    packages=find_packages(exclude='tests'),
    license='BSD',
    url='https://github.com/aol/hammer',
    description=desc,
    long_description=long_desc,
    scripts=[],
    include_package_data=True,
    install_requires=requires,
    keywords = [
        'Configuration Management',
        'IANA',
        'IEEE',
        'IP',
        'IP Address',
        'IPv4',
        'IPv6',
        'Firewall',
        'Network Automation',
        'Networking',
        'Network Engineering',
        'Network Configuration',
        'Systems Administration',
        'Switch',
    ],
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Framework :: Pyramid',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Telecommunications Industry',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet',
        'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
        'Topic :: Security',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Networking',
        'Topic :: System :: Networking :: Monitoring',
        'Topic :: System :: Operating System',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    cmdclass={
        'clean': CleanCommand
    }
)
