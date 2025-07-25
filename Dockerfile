# Use Python 3.10 base image
FROM python:3.10-slim

# Set working directory inside container
WORKDIR /app

# Install OS dependencies (for pip, charts, etc.)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev python3-dev build-essential && \
    apt-get clean

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project into the container
COPY . .
