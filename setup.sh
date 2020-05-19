#!/usr/bin/env bash -e

# This script creates a Python virtual environment, installs required packages
# available from pip, and further installs the Python cplex package from an
# existing IBM ILOG CPLEX Optimization Studio installation.


PYTHON_VERSION=$(python3 -V | grep -o '[0-9]\+\.[0-9]\+')

# Optimization Studio 12.10 (the latest version as of this writing) supports
# only Python 3.6 and 3.7 and SoCRAtic Logic itself requires Python 3.
if [[ $PYTHON_VERSION != 3.[67] ]]; then
    echo "SoCRAtic Logic requires Python 3.6 or 3.7"
    exit 1
fi

# Create the Python virtual environment if not already present
if [[ ! -d venv ]]; then
    # Attempt to install virtualenv (globally) if not found
    if ! python3 -m pip freeze | grep -q "^virtualenv=="; then
        python3 -m pip install virtualenv
    fi

    python3 -m virtualenv venv
fi

# Switch to the virtual environment's context
. venv/bin/activate

# Install/update required packages
pip install -r requirements.txt


CPLEX_ROOT=CPLEX_Studio*/
CPLEX_PATH=cplex/python/$PYTHON_VERSION/

# Check for a CPLEX installation in the working directory
# TODO: Also check platform-specific standard installer locations
root_matches=($(compgen -G "$CPLEX_ROOT" || true))
if (( ${#root_matches[*]} != 1 )); then
    # If not found (or not unique), prompt for installation location
    read -e -p "Path to IBM ILOG CPLEX Optimization Studio ($CPLEX_ROOT): " root_matches
fi

pushd "$root_matches/$CPLEX_PATH" >/dev/null

# Check for available system architecture installers
# TODO: Automatically select the appropriate installer if possible
arch_matches=($(compgen -G "*/" || true))
if (( ${#arch_matches[*]} == 0 )); then
    echo "No installers found; check CPLEX installation"
    exit 1
elif (( ${#arch_matches[*]} > 1 )); then
    # If not unique, prompt for which to use
    echo "Multiple architecture installers detected:"
    printf '  %s\n' "${arch_matches[@]}"
    read -e -p "Please select one of the above: " arch_matches
fi
cd "$arch_matches"

python3 setup.py install

popd >/dev/null
