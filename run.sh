#!/bin/bash

VENV_PATH="/home/neepc/Desktop/detectabee/venv"
MAIN_SCRIPT="/home/neepc/Desktop/detectabee/main.py"
PYTHON="/usr/bin/python3"  # Python do sistema
PYTHON_VERSION=$($VENV_PATH/bin/python -c "import sys; print('python{}.{}'.format(sys.version_info.major, sys.version_info.minor))")
SITE_PACKAGES="$VENV_PATH/lib/$PYTHON_VERSION/site-packages"

echo "[RUNNING] com Python do sistema: $PYTHON"
echo "[USANDO pacotes do venv]: $SITE_PACKAGES"

sudo PYTHONPATH="$SITE_PACKAGES" "$PYTHON" "$MAIN_SCRIPT"
