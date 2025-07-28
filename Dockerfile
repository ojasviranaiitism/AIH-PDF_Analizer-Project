# --- Base Image ---
# Requirement: Use a linux/amd64 architecture.
FROM --platform=linux/amd64 python:3.9-slim

# --- Set Working Directory ---
WORKDIR /app

# --- Install Dependencies ---
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu

COPY ./models /app/models

COPY ./src /app/src

CMD ["python", "src/main.py"]