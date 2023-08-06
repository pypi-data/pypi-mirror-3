try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import sys
import os

sys.path.insert(0, os.getcwd())

package_name = 'tdm_loader'
pkg = __import__(package_name)

try:
    long_description = open('README.rst', 'rb').read()
except:
    long_description = ''

setup(name=package_name,
      version = pkg.__version__,
      author = 'Josh Ayers',
      author_email = 'josh.ayers (at) gmail.com',
      url = 'https://bitbucket.org/joshayers/tdm_loader',
      license = 'MIT',
      description = ('Open National Instruments TDM/TDX files as '
                     'NumPy structured arrays.'),
      long_description = long_description,
      packages = ['tdm_loader'],
      classifiers = ['Development Status :: 4 - Beta',
                     'Programming Language :: Python :: 2.7',
                     'License :: OSI Approved :: MIT License',
                     'Operating System :: OS Independent',
                     'Intended Audience :: End Users/Desktop',
                     'Intended Audience :: Science/Research']
      )

