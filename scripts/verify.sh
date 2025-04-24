#!/bin/bash
# Simple script to run verification using the Makefile

set -e  # Exit on error

# Parse arguments
CHECK_MODE=false
while [[ "$#" -gt 0 ]]; do
  case $1 in
    --check) CHECK_MODE=true ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

# Run the appropriate make target
if [ "$CHECK_MODE" = true ]; then
  echo "Running verification in check mode (for CI)..."
  make verify-check
else
  echo "Running verification in fix mode (for local development)..."
  make verify
fi

echo -e "\n✅ Verification complete!" 