import os
from setuptools import setup, find_packages
 
setup(name='pending-updates',
    version="0.1",
    description='Context manager and utilities for delaying and aggregating function calls',
    author='Matti Haavikko',
    author_email='haavikko@gmail.com',
    url='http://github.com/haavikko/pending-updates',
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
