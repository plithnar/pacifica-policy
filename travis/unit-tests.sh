#!/bin/bash
coverage run --include='policy/*' -m unittest discover -v
coverage report -m
codeclimate-test-reporter
