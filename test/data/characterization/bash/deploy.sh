#!/bin/bash
set -euo pipefail

for file in *.txt; do
    echo "processing $file"
    wc -l "$file"
done
