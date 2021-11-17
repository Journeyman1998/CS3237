import sys
sys.path.append("/home/ubuntu/iot/")
from settings import MQTT_HUMIDITY, USERNAME, PASSWORD, HOST_ADDRESS
from broker import MQTT_Broker


add_humidity_to_db_sql = """
    INSERT INTO humidity(value) VALUES(?);
"""

if __name__ == "__main__":
    client = MQTT_Broker(USERNAME, PASSWORD, HOST_ADDRESS, add_humidity_to_db_sql, MQTT_HUMIDITY)
    client.run()