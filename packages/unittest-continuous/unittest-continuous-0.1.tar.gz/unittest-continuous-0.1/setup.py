from distutils.core import setup
from setuptools import find_packages

from unittest_continuous import __version__

setup(
    name='unittest-continuous',
    version="0.1",
    description="Monkey patches the python unittest module to send results to continuous.io",
    author="Adam Charnock",
    author_email="adam@playnice.ly",
    url="https://github.com/continuous/unittest-continuous",
    license="Apache Software License",
    
    install_requires=[],
    
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.6",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    packages=find_packages()
)