# Use Python 3.12 slim image as base
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HOTEL_DATA_DIR=/app/data

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final stage
FROM python:3.12-slim

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set working directory
WORKDIR /app

# Create data directory
RUN mkdir -p /app/data/csv && chown -R appuser:appuser /app/data

# Copy wheels from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .

# Install wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY . .

# Copy data file (using the correct relative path)
COPY ./data/csv/Copenhagen_hotels_clean.csv /app/data/csv/

# Set ownership of application files
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
