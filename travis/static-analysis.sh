#!/bin/bash
pylint --rcfile=pylintrc policy
pylint --rcfile=pylintrc PolicyServer.py
radon cc policy
