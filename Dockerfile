FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1
ARG REQUIREMENT_FILE

RUN apt-get update

RUN mkdir /code
WORKDIR /code

COPY $REQUIREMENT_FILE /code/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /code/requirements.txt

# Run collectstatic during the build process
COPY . /code/
RUN python3 manage.py collectstatic --noinput
