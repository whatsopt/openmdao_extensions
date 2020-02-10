"""
Author: Remi Lafage <remi.lafage@onera.fr>

This package is distributed under Apache 2 license.
"""

from setuptools import setup

from os import path
from io import open

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

CLASSIFIERS = """
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved :: Apache Software License
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: Microsoft :: Windows
Operating System :: Unix
Operating System :: MacOS
"""

metadata = dict(
    name="openmdao_extensions",
    version="0.4.0",
    description="Additional solvers and drivers for OpenMDAO framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rémi Lafage",
    author_email="remi.lafage@onera.fr",
    license="Apache License, Version 2.0",
    classifiers=[_f for _f in CLASSIFIERS.split("\n") if _f],
    packages=["openmdao_extensions"],
    install_requires=["openmdao"],
    python_requires="!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
    zip_safe=True,
    url="https://github.com/OneraHub/opendmao_extensions",
    download_url="https://github.com/OneraHub/openmdao_extensions/releases",
)

setup(**metadata)
