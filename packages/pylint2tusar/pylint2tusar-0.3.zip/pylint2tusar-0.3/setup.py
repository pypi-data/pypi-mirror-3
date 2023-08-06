# Copyright (c) 2012 Thales Global Services SAS
# 
# Author : Robin Jarry
# 
# The MIT license. See LICENSE file for details

from setuptools import setup, find_packages
import pylint2tusar


setup(
    name='pylint2tusar',
    version=pylint2tusar.__version__,
    url='http://pypi.python.org/pypi/pylint2tusar',
    download_url='http://pypi.python.org/pypi/pylint2tusar',
    license='MIT',
    author='Robin Jarry',
    author_email='robin.jarry@gmail.com',
    description='PyLint plugin to allow TUSAR output format',
    long_description=open('README', 'r').read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Documentation',
        'Topic :: Text Processing',
        'Topic :: Utilities',
    ],
    platforms='any',
    packages=find_packages(exclude=['test']),
    include_package_data=True,
    install_requires=['pylint>=0.25'],
)
