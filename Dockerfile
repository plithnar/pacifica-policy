FROM python:2-onbuild
EXPOSE 8181
CMD [ "python", "./PolicyServer.py" ]
