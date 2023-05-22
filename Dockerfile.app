FROM python:3.7.9-slim-buster

WORKDIR /app


RUN apt-get update && \
    apt-get install -y python3-dev gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements/local.txt

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1