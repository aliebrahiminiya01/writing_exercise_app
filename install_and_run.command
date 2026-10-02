#!/bin/bash
cd "$(dirname "$0")"
python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo
    echo "Installation failed. Please copy the error above."
    read -r -p "Press Return to close."
    exit 1
fi
python3 app.py
