# Use official Python image
FROM python:3.11

# Set working directory inside container
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary backend files
COPY api ./api
COPY alembic.ini ./
COPY .env ./

# Default command (for celery worker); can be overridden in docker-compose
CMD ["celery", "-A", "api.tasks.celery_worker.celery_app", "worker", "--loglevel=info"]
