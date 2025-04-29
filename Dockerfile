# Use a slim Python 3.12.3 image as base
FROM python:3.12.3-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy your application code
COPY . .

# Set the environment variable to run Flask
ENV FLASK_APP=api.py

# Expose the port (default Flask port 5000)
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
