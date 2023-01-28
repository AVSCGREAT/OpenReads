#!/bin/bash
# This script does the setup needed for Gitpod

# Setup pre-commit hooks
pyenv install 3.11 --skip-existing # should match .pre-commit-config.yaml
pyenv global 3.11
python3 -m pip install pre-commit
pre-commit install --install-hooks
git commit
