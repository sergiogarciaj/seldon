FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if needed (e.g., for pandas/db-dtypes)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Default command runs the SQL execution script
CMD ["python", "run_sql.py"]
