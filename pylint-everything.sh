#!/bin/bash -xe

pylint --rcfile=pylintrc policy
coverage run --include='policy/*' test.py -v
coverage report -m
