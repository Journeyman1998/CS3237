import sys
sys.path.append("/home/ubuntu/iot/")
from settings import USERNAME, PASSWORD, MQTT_INTENSITY, HOST_ADDRESS
from broker import MQTT_Broker


add_intensity_to_db_sql = """
    INSERT INTO intensity(value) VALUES(?);
"""

if __name__ == "__main__":
    client = MQTT_Broker(USERNAME, PASSWORD, HOST_ADDRESS, add_intensity_to_db_sql, MQTT_INTENSITY)
    client.run()