#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.txt') as file:
    long_description = file.read()

with open('CHANGES') as file:
    long_description += file.read()

setup(name='agpy',
      version='0.1.2',
      description='agpy, Adam Ginsburg\'s Python Code (in 0.1 for perpetuity - it won\'t bump up until I release something)',
      long_description=long_description,
      author='Adam Ginsburg',
      author_email='adam.ginsburg@colorado.edu',
      data_files=[('h2fit',['h2fit_support/atran.txt',
        'h2fit_support/atran2000.fits',
        'h2fit_support/atran_arcturus.txt',
        'h2fit_support/atran_raw_arcturus.txt',
        'h2fit_support/atran_solar.txt',
        'h2fit_support/atran_tran.txt',
        'h2fit_support/dalgarno1984_table5.txt',
        'h2fit_support/linelist.txt'])],
      url='http://code.google.com/p/agpy/',
      packages=['agpy','agpy/mpfit','AG_fft_tools','AG_image_tools','plfit','contributed','radex'],
     )
