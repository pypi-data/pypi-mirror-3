import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist bdist_egg upload')
    sys.exit()
            
required = ['elementtree>=0.0.7',
        'requests>=0.10.6',]

setup(
    name = 'basecamp',
    version = '0.0.12',
    author = 'Matias Saguir',
    author_email = 'mativs@gmail.com',
    description = ('Almost complete warapper around the Basecamp API. '
                  ),
    license = "MIT",
    keywords = "basecamp api",
    url = 'https://github.com/nowherefarm/basecamp',
    packages=['basecamp'],
    install_requires=required,
    long_description=read('README.md'),
    include_package_data = True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Bug Tracking',
    ],
)
