# -*- coding: utf-8 -*-
from distutils.core import setup


VERSION = __import__("idios").__version__


setup(
    name = "geonode-profiles",
    version = VERSION,
    author = "Ariel Núñez",
    author_email = "ingenieroariel@gmail.com",
    description = "A fork of Idios, to be customized for Geonode",
    long_description = open("README.rst").read(),
    license = "BSD",
    url = "http://github.com/ingenieroariel/geonode-profiles",
    packages = [
        "idios",
        "idios.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)
