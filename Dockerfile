FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Expose port (default for uvicorn)
EXPOSE 8000

# Start server using uvicorn correctly (server.py defines "app")
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
