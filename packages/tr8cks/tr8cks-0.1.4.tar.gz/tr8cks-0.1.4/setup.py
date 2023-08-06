from setuptools import setup, find_packages
import sys, os

version = '0.1.4'
scripts_to_install = [os.path.join(dirname, filename) for dirname, dirnames, filenames in os.walk('bin') for filename in filenames]

setup(name='tr8cks',
      version=version,
      description="Python wrapper for the 8tracks.com ReSTful API",
      url="https://github.com/wh1tney/tr8cks",
      author="Whitney O'Banner",
      author_email='wobanner@gmail.com',
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          "requests",
          "nose",
          "simplejson",
      ],
      scripts=scripts_to_install
      )
