FROM python:3.7-slim

LABEL maintainer='lucasmalakin <lucas.malakin@gmail.com>'

WORKDIR /flamel

RUN apt-get update && \
    apt-get install -y --reinstall build-essential \
        python3-dev \
        python3-pip \
        awscli \
        curl \
        zip \
        vim

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

RUN python3 setup.py develop --no-deps

RUN export AWS_CLI=$(which aws) && \
    ln -s $AWS_CLI /usr/bin/aws_cli