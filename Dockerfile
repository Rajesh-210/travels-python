# Use official Python slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code and templates
COPY app.py .
COPY templates/ ./templates/

# Expose port 5000
EXPOSE 5000

# Run the Flask app
CMD ["python", "app.py"]
