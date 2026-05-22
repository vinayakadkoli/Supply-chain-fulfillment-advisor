#!/bin/sh
set -e

echo "[custom_build] COMPONENT_TYPE=$COMPONENT_TYPE OUTPUT_PATH=$OUTPUT_PATH"

if [ "$COMPONENT_TYPE" = "hdi-deployer" ]; then
    echo "[custom_build] hdi-deployer: running cds build --production only (no UI needed)"
    ./node_modules/.bin/cds build --production
else
    echo "[custom_build] $COMPONENT_TYPE: ensuring ui workspace deps are installed"
    npm install --workspace=ui --legacy-peer-deps --ignore-scripts
    echo "[custom_build] running ui vite build"
    npm run build --workspace=ui
    echo "[custom_build] running cds build --production"
    ./node_modules/.bin/cds build --production
fi

echo "[custom_build] done"
