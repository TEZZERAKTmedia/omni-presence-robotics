#!/bin/bash
set -e

echo "Starting all backend servers..."


python3 Backend/Server/server.py
python3 Backend/Server/server_usb.py &
AUTO_MODE=1 python3 Backend/Server/Navigation/autonomy_server.py &
python3 Backend/Yolo/Backend/main_server.py 


wait