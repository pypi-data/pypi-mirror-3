from setuptools import setup, find_packages
import os, sys

setup(name='cloudkey',
      version='1.2.6',
      description='Dailymotion Cloud API client library',
      long_description=open("README.txt").read(),
      download_url='https://github.com/dailymotion/cloudkey-py/zipball/1.2.6',
      classifiers=[
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        ],
      keywords=['dailymotion', 'dmcloud', 'cloud', 'cloudkey', 'api', 'sdk'],
      author='Sebastien Estienne',
      author_email='sebastien.estienne@gmail.com',
      url='http://github.com/dailymotion/cloudkey-py',
      license='Apache License, Version 2.0',
      include_package_data=True,
      zip_safe=False,
      py_modules = ['cloudkey',],
      install_requires=[
          'setuptools',
          'simplejson>=2.0.9',
          'pycurl>=7.19.0',
      ],
)
