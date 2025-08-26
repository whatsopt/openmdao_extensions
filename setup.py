"""
Author: Remi Lafage <remi.lafage@onera.fr>

This package is distributed under Apache 2 license.
"""

from setuptools import setup

from os import path
from io import open
from openmdao_extensions import __version__

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

CLASSIFIERS = """
Development Status :: 5 - Production/Stable
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
    version=__version__,
    description="Additional solvers and drivers for OpenMDAO framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Rémi Lafage",
    author_email="remi.lafage@onera.fr",
    license="Apache License, Version 2.0",
    classifiers=[_f for _f in CLASSIFIERS.split("\n") if _f],
    packages=["openmdao_extensions"],
    install_requires=["openmdao>=3.0.0"],
    extras_require={
        "egobox": [
            "egobox>=0.32.0",
        ]
    },
    python_requires=">=3.9",
    zip_safe=True,
    url="https://github.com/OneraHub/openmdao_extensions",
    download_url="https://github.com/OneraHub/openmdao_extensions/releases",
    keywords="openmdao openmdao_driver openmdao_nl_solver",
    entry_points={
        "openmdao_driver": [
            "egoboxegordriver = openmdao_extensions.egobox_egor_driver:EgoboxEgorDriver",
            "onerasegodriver = openmdao_extensions.onera_sego_driver:OneraSegoDriver",
            "openturnsdoedriver = openmdao_extensions.openturns_doe_driver:OpenturnsDOEDriver",
            "salibdoedriver = openmdao_extensions.salib_doe_driver:SalibDOEDriver",
            "smtdoedriver = openmdao_extensions.smt_doe_driver:SmtDOEDriver",
        ],
        "openmdao_nl_solver": [
            "recklessnonlinearblockgs = openmdao_extensions.reckless_nonlinear_block_gs:RecklessNonlinearBlockGS"
        ],
    },
)

setup(**metadata)
