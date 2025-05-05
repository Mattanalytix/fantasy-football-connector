# Python image to use.
FROM python:3.13-alpine

# Set the working directory to /app
WORKDIR /app

# copy the requirements file used for dependencies
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Copy the application code
COPY . .

# Run app.py when the container launches
ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:8080", "app:app"]
