# This is our base image. It's a minimal version of Linux
# that already has Python 3.10 installed.
FROM python:3.10-slim

# Set the working directory inside the container to /app
# This creates the /app folder and makes it our "home".
WORKDIR /app

COPY requirements.txt .

# Install all the libraries from the list
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Tell the container what command to run when it starts
# - Runs on port 8000 inside the container
# - Listens on 0.0.0.0 (required for Docker)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
