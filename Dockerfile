# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app

# Copy the application files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Create an instance directory for SQLite persistence
RUN mkdir -p /app/instance

# Set environment variables
# ENV FLASK_APP=shorturl
# ENV FLASK_ENV=production
# ENV DATABASE_URL=sqlite:///instance/app.db

# Expose the port Gunicorn will run on
EXPOSE 8443

# Command to run Gunicorn with Flask app
CMD ["gunicorn", "--certfile=cert.pem", "--keyfile=key.pem", "-w", "1", "-b", "0.0.0.0:8443", "reisepass:create_app()"]
# gunicorn --certfile=cert.pem --keyfile=key.pem -w 1 -b 0.0.0.0:8000 reisepass:create_app()

