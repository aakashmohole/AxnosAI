FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the proxy server port
EXPOSE 8001

# Command to run the FastAPI proxy server
CMD ["uvicorn", "manage:app", "--host", "0.0.0.0", "--port", "8001"]
