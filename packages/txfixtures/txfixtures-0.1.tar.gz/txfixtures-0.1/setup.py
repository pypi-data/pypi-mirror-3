#! /usr/bin/env python

"""distutils metadata/installer for txfixtures"""


from distutils.core import setup


setup(
    name='txfixtures',
    maintainer='Martin Pool',
    maintainer_email='mbp@canonical.com',
    url='https://launchpad.net/txfixtures',
    description=('Treat Twisted applications as Python test fixtures'),
    version='0.1',
    classifiers=["License :: OSI Approved :: GNU General Public License (GPL)"],
    packages=['txfixtures'],
    )
