#!/usr/bin/env python

from setuptools import setup, find_packages
setup(name='btcnet_info',
        version='0.1.2.4',
        description='BitCoin Network Information Library',
        author='Colin Rice',
        author_email='dah4k0r@gmail.com',
        packages = find_packages(),
        namespace_packages=['btcnet_info'],
        include_package_data = True,
        package_data = { "":["*/*"]},
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
