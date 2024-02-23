# Create an ubuntu docker image with pip, python, and git
# build with `docker build -t ubuntu-pip-python-git .`
# create a container from the image that gets destroyed after use
# `docker run --rm -it -v ./:/biobricks ubuntu-pip-python-git /bin/bash`

FROM python:3.9-slim

# Install pipx
RUN python -m pip install --upgrade pip && \
    pip install pipx && \
    pipx ensurepath

# Use a non-root user for better security
RUN useradd --create-home appuser
USER appuser

# Set the home directory for the appuser
WORKDIR /home/appuser

# Start with a shell by default
CMD ["/bin/bash"]
