#!/usr/bin/env bash

# TODO: fix /libraries
TEMPLATE_FILES=$(find openlibrary/{templates,macros} -name '*.html' | grep -v /libraries | tr '\n' ' ')
pytest --filename="$TEMPLATE_FILES" openlibrary/tests/test_templates.py
