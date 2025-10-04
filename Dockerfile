# Use official Python image
FROM python:3.11-slim-bullseye

# Set work directory
WORKDIR /app

# Install system dependencies required by OpenCV (libGL and friends) plus gcc for builds
# Keep the layer small and clean up apt lists to reduce image size
RUN apt-get update \
	&& apt-get install -y --no-install-recommends \
	   gcc \
	   libgl1-mesa-glx \
	   libglib2.0-0 \
	   libsm6 \
	   libxrender1 \
	   libxext6 \
	   ca-certificates \
	&& rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port (Cloud Run expects 8080)
EXPOSE 8080

# Use shell form so ${PORT} is expanded at runtime by Cloud Run
ENV PORT=8080
ENTRYPOINT ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
