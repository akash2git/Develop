# Use an official Python runtime as a parent image
FROM python:3.10.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port 8000
EXPOSE 7600

# Command to run the application
CMD ["gunicorn", "--bind", "0.0.0.0:7600", "social_network.wsgi:application"]
