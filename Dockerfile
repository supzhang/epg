# Use a smaller Alpine Linux base image
FROM python:3.9-alpine

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory to /app
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN apk update \
    && apk add mariadb-dev build-base \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apk del build-base

# Copy the current directory contents into the container at /app
COPY . /app

ENV DJANGO_SETTINGS_MODULE=epg.settings

# Expose port 8000 for the Django app
EXPOSE 8000

# Run the command to start the Django app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
