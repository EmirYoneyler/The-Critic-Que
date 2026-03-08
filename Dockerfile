# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirments.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirments.txt

# Copy the entire project
COPY backend/ ./backend/

# Expose the port FastAPI will run on
EXPOSE 6767

# Run the application
CMD ["python", "-m", "uvicorn", "backend.src.main:app", "--host", "0.0.0.0", "--port", "6767"]
