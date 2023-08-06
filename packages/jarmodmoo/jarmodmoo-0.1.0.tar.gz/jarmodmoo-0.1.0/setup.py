# coding=utf-8
from setuptools import setup

setup(name="jarmodmoo",
      version="0.1.0",
      description="ØMQ Majordomo protocol",
      author="Simon Pantzare",
      author_email="simon+jarmodmoo@pewpewlabs.com",
      url="https://github.com/pilt/jarmodmoo/",
      packages=["jarmodmoo"],
      package_dir={
          "jarmodmoo": "jarmodmoo",
          },
      package_data={
          "jarmodmoo": ["*.cfg"],
          },
      license="MIT",
      platforms="Posix; MacOS X; Windows",
      classifiers = [
          "Development Status :: 3 - Alpha",
          "Topic :: Internet",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          ],
      install_requires=[
          'pyzmq>=0.12.1',
          ])
