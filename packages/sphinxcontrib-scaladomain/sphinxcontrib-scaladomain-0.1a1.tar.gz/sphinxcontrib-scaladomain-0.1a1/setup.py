# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from sphinxcontrib import scaladomain
import sys

with open('README') as stream:
    long_desc = stream.read()

requires = ['Sphinx>=1.0']

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(
    name='sphinxcontrib-scaladomain',
    version=scaladomain.__release__,
    url='http://bitbucket.org/birkenfeld/sphinx-contrib',
    download_url='http://pypi.python.org/pypi/sphinxcontrib-scaladomain',
    license='BSD',
    author='Georges Discry',
    author_email='georges@discry.be',
    description='Sphinx domain for Scala APIs',
    long_description=long_desc,
    zip_safe=False,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Documentation',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    namespace_packages=['sphinxcontrib'],
    **extra
)
