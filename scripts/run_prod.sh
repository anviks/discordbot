#!/bin/bash

# Define the project root directory
project_root="$PWD/.."

# Add the project root directory to the PYTHONPATH
export PYTHONPATH="$project_root"

cd "$project_root" || exit

venv_scripts="$project_root/.venv/bin"

# Copy the .env.production file to .env
cp "$project_root/.env.production" "$project_root/.env"

# Define the translation directory and languages
translations_directory="$project_root/resources/translations"
languages=("en" "et")
domain="messages"

# Loop through each language
for lang in "${languages[@]}"; do
    msgfmt -o "$translations_directory/$lang/LC_MESSAGES/$domain.mo" "$translations_directory/$lang/LC_MESSAGES/$domain.po"
done

# Install required packages using pip
"$venv_scripts/pip" install -r "$project_root/requirements.txt"

# Run the main Python script
"$venv_scripts/python" -m "src.main"
