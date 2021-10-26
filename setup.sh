#!/usr/bin/env bash
set -e

# This script creates a Python virtual environment, installs required packages
# available from pip, and further installs the Python cplex package from an
# existing IBM ILOG CPLEX Optimization Studio installation.


PYTHON_VERSION=$(python3 -V | grep -o '[0-9]\+\.[0-9]\+')

# Create the Python virtual environment if not already present
if [[ ! -d venv ]]; then
    # Attempt to install the virtualenv package (globally) if not found
    if ! python3 -m pip freeze | grep -q "^virtualenv=="; then
        python3 -m pip install virtualenv
    fi

    python3 -m virtualenv venv
fi

source venv/bin/activate
pip install -r requirements.txt


CPLEX_ROOT=CPLEX_Studio
CPLEX_PATH=cplex/python/$PYTHON_VERSION

# Check for a CPLEX installation in the working directory
# TODO: Also check platform-specific standard installer locations
root_matches=("$CPLEX_ROOT"*)  # Glob
if (( ${#root_matches[*]} != 1 )); then
    read -erp "Path to IBM ILOG CPLEX Optimization Studio ($CPLEX_ROOT*): " root_matches
fi

pushd "$root_matches/$CPLEX_PATH" >/dev/null

# Check for available system architecture installers
arch_matches=(*)  # Glob
if (( ${#arch_matches[*]} > 1 )); then
    echo "Multiple architecture installers detected:"
    printf '  %s\n' "${arch_matches[@]}"
    read -erp "Please select one of the above: " arch_matches
fi

cd "$arch_matches"
python3 setup.py install
popd >/dev/null
