# Use an official Debian base image with Python 3.9.10
FROM python:3.9.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt /usr/src/app/

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the remaining application files into the container
COPY . .

# Create a volume for persistent data
VOLUME /usr/src/app/logs

# Expose port 8010
EXPOSE 80

# Run server_Socket.py when the container launches
CMD ["python", "./main.py"]