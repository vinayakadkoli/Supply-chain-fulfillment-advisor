#!/bin/sh
# cache-bust: 2026-05-22-v4-copy-to-outputs
set -e

echo "[custom_build] COMPONENT_TYPE=$COMPONENT_TYPE OUTPUT_PATH=$OUTPUT_PATH"

if [ "$COMPONENT_TYPE" = "hdi-deployer" ]; then
    echo "[custom_build] hdi-deployer: running cds build --production"
    ./node_modules/.bin/cds build --production

    echo "[custom_build] gen/ contents after build:"
    ls -la gen/ || echo "(gen/ not found)"
    echo "[custom_build] gen/db contents:"
    ls -la gen/db/ || echo "(gen/db not found)"

    # Copy gen/db output to /outputs as required by the build framework
    if [ -d gen/db ] && [ -n "$(ls -A gen/db 2>/dev/null)" ]; then
        echo "[custom_build] Copying gen/db contents to /outputs"
        cp -r gen/db/. /outputs/
        echo "[custom_build] /outputs contents:"
        ls -la /outputs/
    else
        echo "[custom_build] ERROR: gen/db is empty or missing after cds build"
        ls -la gen/ 2>/dev/null || echo "(gen/ missing)"
        exit 1
    fi

elif [ "$COMPONENT_TYPE" = "srv" ]; then
    echo "[custom_build] srv: running cds build --production"
    ./node_modules/.bin/cds build --production

    echo "[custom_build] gen/srv contents after build:"
    ls -la gen/srv/ || echo "(gen/srv not found)"

    # Copy gen/srv output to /outputs as required by the build framework
    if [ -d gen/srv ] && [ -n "$(ls -A gen/srv 2>/dev/null)" ]; then
        echo "[custom_build] Copying gen/srv contents to /outputs"
        cp -r gen/srv/. /outputs/
        echo "[custom_build] /outputs contents:"
        ls -la /outputs/
    else
        echo "[custom_build] ERROR: gen/srv is empty or missing after cds build"
        ls -la gen/ 2>/dev/null || echo "(gen/ missing)"
        exit 1
    fi

else
    echo "[custom_build] $COMPONENT_TYPE: installing ui workspace deps"
    npm install --workspace=ui --legacy-peer-deps --ignore-scripts
    echo "[custom_build] running ui vite build"
    npm run build --workspace=ui
    echo "[custom_build] running cds build --production"
    ./node_modules/.bin/cds build --production

    echo "[custom_build] gen/srv contents after build:"
    ls -la gen/srv/ || echo "(gen/srv not found)"

    if [ -d gen/srv ] && [ -n "$(ls -A gen/srv 2>/dev/null)" ]; then
        cp -r gen/srv/. /outputs/
    fi
fi

echo "[custom_build] done"
