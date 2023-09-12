# Use the official Python image as a parent image
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Define environment variables for PostgreSQL
ENV POSTGRES_HOST=postgres-flask-db.postgres.database.azure.com
ENV POSTGRES_PORT=5432
ENV POSTGRES_DB=postgres
ENV POSTGRES_USER=demodomain
ENV POSTGRES_PASSWORD=World&147

# Start the Flask application
CMD ["python", "gunicorn", "--bind", "0.0.0.0:5000", "app.py"]
