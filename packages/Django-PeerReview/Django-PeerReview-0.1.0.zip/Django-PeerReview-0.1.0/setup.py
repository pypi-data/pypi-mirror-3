#/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-PeerReview",
    version = "0.1.0",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Simple reusable app for management of peer review of arbitrary django models."),
    license = "Modified BSD",
    keywords = "peer review arbitrary django models",
    url = "https://bitbucket.org/weholt/django-peer-review",
    zip_safe = False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        ],
    long_description=read('README.txt'),
    include_package_data = True,
    packages = ['peerreview'],
    install_requires=[
        "Django >= 1.4.0",
        ],
)

