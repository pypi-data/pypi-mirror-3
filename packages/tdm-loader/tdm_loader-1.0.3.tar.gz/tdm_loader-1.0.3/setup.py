try:
    from setuptools import setup
    setuptools_available = True
except ImportError:
    from distutils.core import setup
    setuptools_available = False
import sys
import os


current_dir = os.getcwd()
sys.path.insert(0, current_dir)


requires = ['numpy>=1.5']

package_name = 'tdm_loader'
with open(os.path.join(current_dir, package_name, 'VERSION'), 'rb') as fobj:
    version = fobj.read().strip()

try:
    long_description = open(os.path.join(current_dir, 'README.txt'),
                            'rb').read()
except:
    long_description = ''

# these files will be installed with the package
# they must also appear in MANIFEST.in
data_files = ['VERSION']

kwargs = dict(
    name = package_name,
    version = version,
    author = 'Josh Ayers',
    author_email = 'josh.ayers (at) gmail.com',
    url = 'https://bitbucket.org/joshayers/tdm_loader',
    license = 'MIT',
    description = ('Open National Instruments TDM/TDX files as '
                   'NumPy structured arrays.'),
    long_description = long_description,
    packages = [package_name],
    package_data = {package_name:data_files},
    classifiers = ['Development Status :: 4 - Beta',
                   'Programming Language :: Python :: 2.7',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Intended Audience :: End Users/Desktop',
                   'Intended Audience :: Science/Research'])

if setuptools_available:
    kwargs.update(dict(
        install_requires = requires))

setup(**kwargs)

