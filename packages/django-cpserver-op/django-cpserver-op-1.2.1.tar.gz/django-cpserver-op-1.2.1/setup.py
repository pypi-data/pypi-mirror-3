#from distutils.core import setup
from setuptools import setup
import os, os.path

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="django-cpserver-op",
    version="1.2.1",
    description="Management commands for serving Django via CherryPy's built-in WSGI server modified for OpenProximity",
    author="Peter Baumgartner",
    author_email="pete@lincolnloop.com",
    url="https://github.com/OpenProximity/django-cpserver",
    packages=[
        "django_cpserver",
        "django_cpserver.management",
        "django_cpserver.management.commands",
    ],
    license="BSD",
    long_description=read("README.rst"),
    install_requires=['CherryPy'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: CherryPy",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
    ]
)
