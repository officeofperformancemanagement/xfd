#!/bin/sh -e

# wipe away any previous builds
rm -fr dist xfd.egg-info Pipfile Pipfile.lock

# make sure libraries used for publishing are up to date
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel twine
python3 -m pip install --upgrade twine

python3 setup.py sdist
