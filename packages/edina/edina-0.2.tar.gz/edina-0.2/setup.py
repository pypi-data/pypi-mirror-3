from setuptools import setup, find_packages

import edina
import os
import sys

setup(name='edina',
      version=edina.get_version(),
      description="EDINA geo python helper",
      author='George Hamilton',
      author_email='george.hamilton@ed.ac.uk',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],
      install_requires=[
        'fabric>=1.0',
        'pep8',
        'virtualenv'
        ],
      )
