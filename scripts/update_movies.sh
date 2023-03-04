#!/bin/sh
export PYENV_VERSION=3.9.5

echo "Updating Movies"
poetry run python3 app/movies_2023.py >logs/movies_2023.log 2>&1
echo "Done"