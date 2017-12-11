#!/usr/bin/python
"""Setup and install the policy."""
from pip.req import parse_requirements
from setuptools import setup

# parse_requirements() returns generator of pip.req.InstallRequirement objects
INSTALL_REQS = parse_requirements('requirements.txt', session='hack')

setup(name='PacificaPolicy',
      version='1.0',
      description='Pacifica Policy',
      author='David Brown',
      author_email='david.brown@pnnl.gov',
      packages=[
          'policy',
          'policy.ingest',
          'policy.ingest.test',
          'policy.reporting',
          'policy.reporting.transaction',
          'policy.status',
          'policy.status.instrument',
          'policy.status.proposal',
          'policy.status.transaction',
          'policy.status.user',
          'policy.test',
          'policy.uploader',
          'policy.uploader.test',
      ],
      entry_point={
          'console_scripts': ['PolicyServer=policy:main'],
      },
      scripts=['PolicyServer.py'],
      install_requires=[str(ir.req) for ir in INSTALL_REQS])
