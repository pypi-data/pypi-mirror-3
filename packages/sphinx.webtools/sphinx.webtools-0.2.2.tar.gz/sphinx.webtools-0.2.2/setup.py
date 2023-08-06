#!/usr/bin/env python
import os
from setuptools import setup

f = open(os.path.join(
            os.path.dirname(__file__),
                'docs', 'source', 'content', 'readme.txt'))
long_description = f.read().strip()
f.close()

sphinx_webtools_url = 'http://bitbucket.org/florent/sphinx-webtools'

packages = [
                'sphinx',
                'sphinx.webtools'
            ]

data_files = [
                'COPYING',
                'README'
            ]

package_data = {
                'sphinx.webtools': ['tests/data/*/*.rst']
                }

setup(
        name='sphinx.webtools',
        description='Sphinx web tools for python web frameworks',
        version='0.2.2',
        url=sphinx_webtools_url,
        license='BSD',
        author='Florent PIGOUT',
        author_email='florent.pigout@gmail.com',
        long_description=long_description,
        install_requires=[
            'Genshi >= 0.5.1',
            'Sphinx >= 0.5.1'
            ],
        namespace_packages=['sphinx.webtools'],
        packages=packages,
        include_package_data=True,
        data_files=data_files,
        package_data=package_data,
        test_suite = 'sphinx.webtools.tests',
    )
