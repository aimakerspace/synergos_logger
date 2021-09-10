#!/usr/bin/env python

####################
# Required Modules #
####################

# Generic/Built-in
import os
from setuptools import setup

###########
# Helpers #
###########

def read(fname):
    with open(
        os.path.join(os.path.dirname(__file__), fname), 
        encoding='utf-8'
    ) as f:
        return f.read()

setup(
    name="synergos_logger",
    version="0.1.0",
    author="AI Singapore",
    author_email='synergos-ext@aisingapore.org',
    description="Logging component of the Synergos network",
    long_description=read('README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Topic :: Scientific/Engineering :: Image Processing',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords="synergos horizontal vertical federated learning logging graylog",
    url="https://github.com/aimakerspace/synergos_logger.git",
    license="MIT",

    packages=["synlogger"],
    python_requires = ">=3.7",
    install_requires=[
        "psutil==5.7.0",
        "pygelf==0.3.6",
        "structlog==20.1.0",
        "graypy==2.1.0"
    ],
    include_package_data=True,
    zip_safe=False
)
