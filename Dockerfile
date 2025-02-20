FROM python:3.11-slim

WORKDIR /app/bot
COPY requirements.txt /app/bot
COPY . /app/bot