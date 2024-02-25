# Create an ubuntu docker image with pip, python, and git
# build with `docker build -t ubuntu-pip-python-git -f ./docker/Dockerfile .`
# create a container from the image that gets destroyed after use
# `docker run --rm -it -v ./:/home/appuser/biobricks ubuntu-pip-python-git /bin/bash`

FROM python:3.9-slim

# Install system dependencies including Git
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install pipx
RUN python -m pip install --upgrade pip && \
    pip install pipx && \
    pipx ensurepath

# Use a non-root user for better security
RUN useradd --create-home appuser
USER appuser

# Set the home directory for the appuser
WORKDIR /home/appuser

# install the requirements.txt
COPY requirements.txt /home/appuser
RUN pip install -r requirements.txt

# add environmental variables from .env file
COPY .env /home/appuser

# Start with a shell by default
CMD ["/bin/bash"]
