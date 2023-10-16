#!/usr/bin/env python
from setuptools import setup, find_packages

MODULE_NAME = "flamel"  # package name used to install via pip (as shown in `pip freeze` or `conda list`)
MODULE_NAME_IMPORT = "flamel"  # this is how this module is imported in Python (name of the folder inside `src`)
REPO_NAME = "flamel"  # repository name


def requirements_from_pip(filename="requirements.txt"):
    with open(filename, "r") as pip:
        return [l.strip() for l in pip if not l.startswith("#") and l.strip()]


core_deps = requirements_from_pip()
all_deps = core_deps
author = "lucasmalakin"

setup(
    name=MODULE_NAME,
    description=REPO_NAME,
    url="https://github.com/{}/{}".format(author, REPO_NAME),
    author=author,
    package_dir={"": "src"},
    packages=find_packages("src"),
    version="0.0.1",
    install_requires=core_deps,
    extras_require={"all": all_deps},
    include_package_data=True,
    zip_safe=True,
)
