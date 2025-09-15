FROM python:3.12-slim

WORKDIR /app

# Copy requirements from code folder
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app
COPY . .

EXPOSE 5000

# Use run.py as entrypoint
CMD ["python", "run.py"]