import os
import sys
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = read("requirements.txt").split("\n")
if sys.version_info < (2,6):
    requirements.append('simplejson')
    
setup(
    name = "python-socialtext",
    version = "0.2.0",
    description = "Python binding for the Socialtext REST API",
    long_description = read('README.rst'),
    author = 'Justin Murphy, The Hanover Insurance Group',
    author_email = 'ju1murphy@hanover.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires = requirements,
    
    tests_require = ["nose", "mock"],
    test_suite = "nose.collector",
    
    entry_points = {
        'console_scripts': ['socialtext = socialtext.shell:main']
    }
)