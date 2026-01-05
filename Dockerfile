# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables to prevent bytecode generation and buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose the port
EXPOSE 5000

# Run with Gunicorn for production-grade stability (or run.py for simplicity if gunicorn not added)
# Since we haven't added gunicorn to requirements yet, let's use python run.py for now
# Ideally we should add gunicorn later.
CMD ["python", "run.py"]
