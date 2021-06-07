FROM python:3.8
RUN useradd -rm -d /home/myuser -s /bin/bash -g root -G sudo -u 1001 myuser

RUN apt update && \
    apt install python3-pip git -y && \
    pip3 install pipenv
    

# set environment variables
ENV PYTHONUNBUFFERED 1
# ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBUG 0

RUN mkdir /code
WORKDIR /code
ADD . /code/


RUN pipenv install
# installed django in via pipfile.lock already
RUN pipenv install django
# USER myuser
