#!/usr/bin/env bash
set -euo pipefail

mkdir -p assets/vendor assets/data

curl -L --fail -o assets/vendor/d3.v7.min.js \
  https://d3js.org/d3.v7.min.js

curl -L --fail -o assets/vendor/topojson-client.min.js \
  https://unpkg.com/topojson-client@3/dist/topojson-client.min.js

curl -L --fail -o assets/vendor/d3-composite-projections.min.js \
  https://unpkg.com/d3-composite-projections@1.4.0/d3-composite-projections.min.js

curl -L --fail -o assets/data/provinces.json \
  https://unpkg.com/es-atlas@0.6.0/es/provinces.json

printf '\nDone. The site now uses local files only.\n'
printf 'For local testing: python3 -m http.server 8000\n'
printf 'Then open: http://localhost:8000/\n'
