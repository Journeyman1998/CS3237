import sys
sys.path.append("/home/ubuntu/iot/")
from settings import MQTT_GESTURE_RESULTS, USERNAME, PASSWORD, HOST_ADDRESS
from broker import MQTT_Broker


add_gesture_to_db_sql = """
    INSERT INTO gesture(gesture_type) VALUES(?);
"""

if __name__ == "__main__":
    client = MQTT_Broker(USERNAME, PASSWORD, HOST_ADDRESS, add_gesture_to_db_sql, MQTT_GESTURE_RESULTS)
    client.run()