#!/usr/bin/env python

from sys import version_info

from setuptools import setup, find_packages

python_version = "%s.%s" % (version_info[0], version_info[1])

if python_version == "2.6":
    requires = ["orderedmultidict>=0.7", "ordereddict>=1.1"]
else:
    requires = ["orderedmultidict>=0.7"]

setup(
    name="htpasswd",
    version="2.0",
    packages=["htpasswd"],
    install_requires=requires,
    author="Ilya A. Otyutskiy",
    author_email="sharp@thesharp.ru",
    maintainer="Ilya A. Otyutskiy",
    url="https://github.com/thesharp/htpasswd",
    description="Library to work with htpasswd user (basic authorization) "
                "and group files.",
    license="MIT"
)
