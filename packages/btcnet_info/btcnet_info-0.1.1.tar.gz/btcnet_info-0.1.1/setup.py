#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='btcnet_info',
        version='0.1.1',
        description='BitCoin Network Information Library',
        author='Colin Rice',
        author_email='dah4k0r@gmail.com',
        packages = find_packages(),
        include_package_data = True,
        package_data = { "":["pools/*", "difficulty_sites/*", "coins/*", "exchanges/*"]},
        url='github.com/c00w/btcnet_info',
        classifiers=[
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'Topic :: System :: Networking',
            'License :: OSI Approved :: MIT License',
            ],
        license = 'MIT Expat License',
        install_requires = ['gevent']
        )
