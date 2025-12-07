# Use a base Python image python:3.10.
FROM python:3.10

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install necessary dependencies from the requirements.txt.
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy your app code into the container.
COPY . .

# Expose the port your Django app runs on (default is 8000).
EXPOSE 8000

# Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
