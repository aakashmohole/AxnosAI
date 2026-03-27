FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for some Python packages like psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install core requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Reinstall user's data science packages from previous Dockerfile
RUN pip install --no-cache-dir \
    scipy \
    scikit-learn \
    matplotlib \
    seaborn

# Copy the rest of the application
COPY . .

# Expose Django port
EXPOSE 8000

# Start development server binding to all interfaces inside container
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
