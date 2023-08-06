import os
import sys
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "mo2s3",
    version = "0.0.1",
    author = "Thomas Sileo",
    author_email = "thomas.sileo@gmail.com",
    description = "A python command line tool that simplify MongoDB backup (mongodump/mongorestore) to Amazon S3.",
    license = "MIT",
    keywords = "aws s3 mongodb backup restore archive",
    url = "http://pypi.python.org/pypi/mo2s3",
    packages=['mo2s3'], # , 'tests'
    long_description= read('README.rst'),
    install_requires=[
        "envoy", "boto", "argparse"
        ],
    entry_points={'console_scripts': ["mo2s3 = mo2s3.core:main"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: System :: Archiving :: Backup",
        "License :: OSI Approved :: MIT License",
    ],
)