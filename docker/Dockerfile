# Create an ubuntu docker image with pip, python, and git
# build with `docker build -t ubuntu-pip-python-git .`
# run with `docker run -it ubuntu-pip-python-git`
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git