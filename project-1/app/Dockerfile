# syntax=docker/dockerfile:1
FROM python:3
# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt
# copy project
COPY . .
RUN mv dummy_pdfs/ /data/
# initialize DB
RUN chmod +x db/*
RUN python db/init_db.py
# set static values in db
RUN python db/init_files_db.py
