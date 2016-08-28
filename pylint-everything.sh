#!/bin/bash -xe

pylint --rcfile=pylintrc policy
coverage run --include='metadata/*' test.py -v
coverage report -m
