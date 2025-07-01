#!/bin/bash

echo "Starting vsxapi"


echo "Starting xdnext"
/app/xdnext server start &

echo "Starting streamlit"

source /app/.venv/bin/activate
cd /app/wui || exit
streamlit run wui/wui.py --server.port 9702
