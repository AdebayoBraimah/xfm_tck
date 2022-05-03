#!/usr/bin/env bash
# -*- coding: utf-8 -*-

# DESCRIPTION:
#   Creates a python virtual environment for development of this package
#   (installed via Anaconda). The environment is intended to have no default
#   packages.
# 
# 
# NOTE:
#   * Currently only works with Anaconda.
#   * Environment setup is for python v3+.
#   * If using a machine without administrative privileges, use ``--user`` 
#     flag during the ``pip install`` step.

if [[ ! -d ../.env ]]; then
  mkdir -p ../.env
fi

# Create environment using conda
conda create -p ../.env/env --no-default-packages --yes

# Activate environment
conda activate ../.env/env

# Install pip
conda install pip --yes

# Install requirements
pip install -r requirements.txt