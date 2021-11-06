# CS3237 Project - AEGIS

The table below describes the key files.

| Files     | Location | Description       |Remarks|
|-----------|----------|-------------------|-------|
|read_sensor/gesture_recorder.py|Office|Records the gesture data and send it to EC2|Change the ADDRESS variable to your sensortag's address|
|read_sensor/humidity_recorder.py|Home|Records the soil humidity level and send it to EC2|Change the ADDRESS variable to your sensortag's address|
|ec2/classify.py|EC2|Classifies the gesture data into its type||
|flask/gesture_broker.py|EC2|Receives the gesture results and save it in the SQL database||
|flask/humidity_broker.py|EC2|Receives the humidity values and save it in the SQL database||
|flask/run.py|EC2|A Flask RESTful server that receives uploaded images and sends requested data from phone app||
