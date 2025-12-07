FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps (if any required later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy repository into container
COPY . /app

EXPOSE 80

# Use gunicorn to serve the Flask app
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app", "--workers", "1", "--threads", "4"]
