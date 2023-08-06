#!/usr/bin/env python

from setuptools import setup, find_packages
version = '1.0'

if __name__ == '__main__':
    setup(name='pytailf',
          version=version,
          description='Simple python tail -f wrapper',
          author='Alexey Loshkarev',
          author_email='elf2001@gmail.com',
          url='https://bitbucket.org/angry_elf/pytailf/',
          packages=find_packages(),
          license='GPL',
          classifiers=[
              "Development Status :: 4 - Beta",
              "Intended Audience :: Developers",
              "License :: OSI Approved :: GNU General Public License (GPL)",
              "Natural Language :: English",
              "Programming Language :: Python",
              "Topic :: Software Development :: Libraries :: Python Modules",
              ],
          )
