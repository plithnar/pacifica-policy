#!/bin/bash
coverage run --include='policy/*' -m pytest -v
coverage report -m
codeclimate-test-reporter
