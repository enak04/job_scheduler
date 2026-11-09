FROM python:3.12-slim

WORKDIR /app

# Installed before copying the code so that code changes reuse this cached layer.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scheduler ./scheduler

# Print logs immediately instead of buffering them.
ENV PYTHONUNBUFFERED=1
