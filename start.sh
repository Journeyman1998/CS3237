#!bin/bash

(trap 'kill 0' SIGINT;
python ml/classifier.py &
python flask_server/humidity_broker.py &
python flask_server/gesture_broker.py &
python flask_server/optical_broker.py &
python flask_server/run.py)