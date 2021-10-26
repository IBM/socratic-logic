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

# Path to Python utilities within CPLEX application directory
CPLEX_PYTHON_PATH="cplex/python"

# Helper to test if Python satisfies minimum version requirements
# Usage: check_python PYTHON VERSION [MINOR_VERSION...]
check_python() {
  local python="$1"; shift; local IFS=. v; v=$(tr -s . , <<< "$*.")
  "$python" -c "import sys; exit(not sys.version_info[:3] >= ($v))"
}


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


# Just go with the virtual environment if already present
if [[ ! -d venv ]]; then
  pushd "$cplex_root/$CPLEX_PYTHON_PATH" >/dev/null

  # Check for versions of Python supported by CPLEX (and SoCRAtic)
  cplex_python_v=(*)  # Glob
  python3=()
  for v in "${cplex_python_v[@]}"; do
    if type -P "python$v" >/dev/null && check_python "python$v" 3.6; then
      python3+=("python$v")
    fi
  done

  popd >/dev/null

  if [[ ${#python3[*]} -eq 1 ]]; then
    echo "Using ${python3[0]}"
  else
    echo "Versions of Python supported by $(basename "$cplex_root"):"
    printf '  %s\n' "${cplex_python_v[@]}"
    read -erp "Command for Python >= 3.6 (python3*): " python3
  fi
fi


# Create the Python virtual environment if not already present
if [[ ! -d venv ]]; then
  # Attempt to install the virtualenv package (globally) if not found
  if ! "$python3" -m pip freeze | grep -q "^virtualenv=="; then
    "$python3" -m pip install virtualenv
  fi

  "$python3" -m virtualenv venv
fi

source venv/bin/activate
pip install -r requirements.txt


python_v="$(python3 -V | grep -o '[0-9]\+\.[0-9]\+')"
pushd "$cplex_root/$CPLEX_PYTHON_PATH/$python_v" >/dev/null

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
