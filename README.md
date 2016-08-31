# Pacifica Policy API
[![Build Status](https://travis-ci.org/EMSL-MSC/pacifica-policy.svg?branch=master)](https://travis-ci.org/EMSL-MSC/pacifica-policy)

This is the Pacifica Policy API and implements policy decisions
for the rest of the Pacifica software.

## Installing the Service

### Use the docker container

```
docker pull pacifica/policy
```

### The Docker Compose Way

```
docker-compose up
```

### The Manual Way

Install the dependencies using pip (or some other similar python way).
```
pip install -r requirements.txt
```

Run the code.
```
python PolicyServer.py
```

## The API

The policy server is split up into endpoints named for their Pacifica
project that utilizes them. So the path `/uploader` is used by the 
Pacifica Uploader (http://github.com/EMSL-MSC/pacifica-uploader) to
control its behavior. The idea is that workflow implemented by the 
various Pacifica projects has some element of site or instance
specific policy that can be applied to the running service. The policy
is driven by the metadata and thus this project should talk to the
metadata service.

### The Uploader Policy API


