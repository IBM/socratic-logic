#!/usr/bin/env bash
set -e

# This script creates a Python virtual environment, installs required packages
# available from pip, and further installs the Python cplex package from an
# existing IBM ILOG CPLEX Optimization Studio installation.


# Default installation paths for all supported platforms
CPLEX_DEFAULT_INSTALL_PATHS=(
  "/mnt/c/Program Files/IBM/ILOG"  # Windows
  "/opt/IBM/ILOG"                  # UNIX
  "/opt/ibm/ILOG"                  # Linux
  "/Applications"                  # macOS
)

# Glob matching versioned CPLEX application directory
CPLEX_GLOB="CPLEX_Studio*"


# Check for CPLEX in pwd and default installation directories
cplex_root=()
for path in . "${CPLEX_DEFAULT_INSTALL_PATHS[@]}"; do
  [[ -d "$path" ]] && while IFS= read -rd $'\0'; do
    cplex_root+=("$REPLY")
  done < <(find "$path" -maxdepth 1 -name "$CPLEX_GLOB" -print0)
done

if (( ${#cplex_root[*]} == 1 )); then
  echo "Using ${cplex_root[0]}"
else
  if (( ${#cplex_root[*]} > 1 )); then
    echo "Multiple CPLEX installations detected:"
    printf '  %s\n' "${cplex_root[@]}"
  fi
  read -erp "Path to IBM ILOG CPLEX Optimization Studio ($CPLEX_GLOB): " cplex_root
fi


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


PYTHON_VERSION=$(python3 -V | grep -o '[0-9]\+\.[0-9]\+')
CPLEX_PATH=cplex/python/$PYTHON_VERSION

pushd "$cplex_root/$CPLEX_PATH" >/dev/null

# Check for available system architecture installers
cplex_arch=(*)  # Glob
if (( ${#cplex_arch[*]} > 1 )); then
  echo "Multiple architecture installers detected:"
  printf '  %s\n' "${cplex_arch[@]}"
  read -erp "Please select one of the above: " cplex_arch
fi

cd "$cplex_arch"
python3 setup.py install
popd >/dev/null
