if [[ "$#" -ne 1 ]]; then
    echo "Usage: $0 <dev|prod>"
    exit 1
fi

script_path=$(dirname "$(realpath -s "$0")")

# Define the project root directory
project_root="$script_path/.."

# Add the project root directory to the PYTHONPATH
export PYTHONPATH="$project_root"

cd "$project_root" || exit

venv_scripts="$project_root/.venv/bin"

if [[ $1 == "dev" ]]; then
    environment=development
elif [[ $1 == "prod" ]]; then
    environment=production

    # Install required packages using pip
    "$venv_scripts/pip" install -r "$project_root/requirements.txt"
else
    echo "Usage: $0 <dev|prod>"
    exit 1
fi

# Copy relevant values to .env
cp "$project_root/.env.$environment" "$project_root/.env"

# Define the translation directory and languages
translations_directory="$project_root/resources/translations"
languages=("en" "et")
domain="messages"

# Loop through each language
for lang in "${languages[@]}"; do
    msgfmt -o "$translations_directory/$lang/LC_MESSAGES/$domain.mo" "$translations_directory/$lang/LC_MESSAGES/$domain.po"
done

# Run the main Python script
"$venv_scripts/python" -m "src.main"
