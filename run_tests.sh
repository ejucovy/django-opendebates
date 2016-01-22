#!/usr/bin/env bash
set -e

find . -name '*.pyc' -delete

find . -name "*.js" -not \( \
    -path "./static/*" -o \
    -path "*/bower_components/*" -o \
    -path "./node_modules/*" -o \
    -path "*/jquery.cookie.js" \) -print0 | xargs -0 jshint

flake8 .

coverage run manage.py test --keepdb "$@"
coverage report -m --fail-under 30  # FIXME: increase minimum requirement to 80 ASAP
