""" Installer
"""
import os
from os.path import join
from setuptools import setup, find_packages

def read(*pathnames):
    """ Read
    """
    return open(os.path.join(os.path.dirname(__file__), *pathnames)).read()

name = 'eea.forms'
path = name.split('.') + ['version.txt']
version = open(join(*path)).read().strip()

setup(name='eea.forms',
        version=version,
        description="EEA forms",
        long_description=(open("README.txt").read() + "\n" +
                          open(os.path.join("docs", "HISTORY.txt")).read()),
        classifiers=[
            "Framework :: Plone",
            "Framework :: Zope2",
            "Programming Language :: Python",
            ],
        keywords='zope plone eea forms',
        author='Zoltan Szabo, European Environment Agency',
        author_email='webadmin@eea.europa.eu',
        url='https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.forms',
        license='GPL',
        packages=find_packages(),
        namespace_packages=['eea'],
        include_package_data=True,
        zip_safe=False,
        install_requires=[
            'setuptools',
            'collective.quickupload',
        ]
        )
