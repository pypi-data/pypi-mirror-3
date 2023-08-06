from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='targetpay',
      version=version,
      description="Python interface to the TargetPay.com payment service provider",
      long_description=open('README.txt').read(),
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
      ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='targetpay payment ideal',
      author='Bram Duvigneau',
      author_email='bram@bramd.nl',
      url='http://www.bitbucket.org/bram/python-targetpay/',
      license='',
      packages=find_packages('.', exclude=['ez_setup', 'examples', 'tests', 'bootstrap']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # -*- Extra requirements: -*-
      ],
      entry_points = {
      }
)
