# Stage 1: Specify the base image with the required platform
# This ensures compatibility with the AMD64 architecture as required.
FROM --platform=linux/amd64 python:3.9-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file and install dependencies
# This keeps the container lean by caching this layer if dependencies don't change.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy all project files into the working directory
# This now includes our scripts AND the local 'model' folder.
COPY . .

# Step 5: Define the command to run the application
# This executes our main script, which handles the input/output directories.
CMD ["python", "main.py"]
