FROM python:3.11-slim

WORKDIR /app

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app:/app/v1_src:$PYTHONPATH

# Install dependencies
COPY v2/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy V1 pipeline source
COPY src/ ./v1_src/

# Copy V2 backend application code
COPY v2/backend/ .

# Run
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
