# Step 1: Base Image
# Use an official, lightweight Python image. 
# 'python:3.11-slim' is a great choice as it's stable and smaller than the full version.
# This creates a self-contained Linux environment with Python 3.11 installed.
FROM python:3.11-slim

# Step 2: Set the Working Directory
# This creates a directory inside the container called `/app` and sets it as the
# default location for all subsequent commands. This keeps your project files organized.
WORKDIR /app

# Step 3: Install Dependencies (Optimized for Docker's Layer Caching)
# First, copy ONLY the requirements.txt file into the container.
# This is a critical optimization. Docker builds in layers. As long as your
# requirements.txt file doesn't change, Docker will reuse the cached layer
# from this step, making future builds much faster.
COPY requirements.txt .

# Now, run pip to install the dependencies listed in requirements.txt.
# --no-cache-dir is a good practice to keep the image size smaller.
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy Application Code
# With the dependencies installed, now copy the rest of your application's
# source code into the /app directory inside the container.
COPY . .

# Step 5: Expose Port (Documentation)
# This line informs Docker that the container listens on port 8000 at runtime.
# It's mainly for documentation purposes. The actual port mapping to your host
# machine is handled in the docker-compose.yml file.
EXPOSE 8000

# NOTE: There is no CMD or ENTRYPOINT here.
# The command to run the application (`uvicorn main:app ...`) is specified
# in your docker-compose.yml file. This is good practice as it separates
# the container build instructions (Dockerfile) from the runtime configuration
# (docker-compose.yml).