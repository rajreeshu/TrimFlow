# Use Python 3.13 as the base image
FROM python:3.13

# Set the working directory
WORKDIR /app

# Install FFmpeg and other required system dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Copy only the requirements file first
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port 8000
EXPOSE 8000

# Default command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]