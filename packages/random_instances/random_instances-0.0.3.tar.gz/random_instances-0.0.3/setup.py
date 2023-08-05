from distutils.core import setup

setup(
    name = "random_instances",
    packages = ["random_instances"],
    package_data={'random_instances': ['*.py']},
    version = "0.0.3",
    description = "Retrieve or generate random instances of Django models.",
    author = "Red Interactive",
    author_email = "geeks@ff0000.com",
    url = "http://ff0000.com/",
    download_url = "https://github.com/ff0000/random_instances",
    keywords = ["django", "admin", "bdd", "tdd", "documentation", "lettuce"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Framework :: Django",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Testing",
        "Topic :: Utilities"
        ],
    long_description = """\
An utility to retrieve or generate random instances of Django models.
-------------------------------------

This module exports a get_or_create_random function that improves Django's
get_or_create (http://djangoproject.com/documentation/models/get_or_create/)
on two aspects:

* invoking get_or_create_random with parameters that match MULTIPLE instances
does not raise an error, but rather returns one of those instances at random

* invoking get_or_create_random with parameters that do not match ANY instance
returns a NEW instance of that model (the same occurs with get_or_create). The
improvement is that get_or_create_random can be invoked without passing a value
for all the 'required' fields of the model. If these fields are not passed,
they are automatically filled with random values (e.g.: CharFields are filled
with random strings, ImageFields with random images).

The goal is to make prototyping faster, as model instances can be obtained and
created by specifying just the minimum set of desired fields. This is useful
when writing tests and can avoid having to write complex fixtures.
"""
)