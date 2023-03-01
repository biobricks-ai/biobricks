# Create an ubuntu docker image with pip, python, and git
# build with `docker build -t ubuntu-pip-python-git .`
# create a container from the image that gets destroyed after use
# `docker run --rm -it ubuntu-pip-python-git /bin/bash`
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    git

# Add R and the remotes package, non-interactively
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update 
RUN apt-get install -y \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \ 
    libfontconfig1-dev \ 
    libfreetype6-dev libpng-dev libtiff5-dev libjpeg-dev \ 
    libharfbuzz-dev libfribidi-dev

# add testthat, covr, fs, purrr, dplyr, and reticulate R packages
RUN R -e "install.packages(c('testthat', 'covr', 'fs', 'purrr', 'dplyr', 'reticulate'))"
RUN R -e "install.packages(c('tidyverse','remotes'))"