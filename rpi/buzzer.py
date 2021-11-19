# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import requests
import ast
import time
import asyncio
import platform
import struct
import paho.mqtt.client as mqtt

global watering
watering = False
global buzz
buzz = False
global value
value = 0
global thresholds
global low_threshold
global high_threshold

USERNAME = "aegis"
PASSWORD = "aegis2021"
RESULTS1 = "aegis/humidity"
RESULTS2 = "aegis/gesture_results"
HOST_ADDRESS = "18.142.17.12"

THRESHOLD_ADDRESS = "http://18.142.17.12:5000/app"

from bleak import BleakClient

def getAppData():
    data = requests.get(THRESHOLD_ADDRESS, timeout=2)

    if data.status_code == 200:
        data = ast.literal_eval(data.text)
        return data
    else:
        return None


def get_threshold():
    global low_threshold
    global high_threshold
    # initialise state
    while True:
        time.sleep(2)
        data = getAppData()
        low_threshold = data['config']['low_threshold']
        high_threshold = data['config']['high_threshold'] 
        return [low_threshold,high_threshold]
        

def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
   
    client.subscribe(RESULTS1)
    client.subscribe(RESULTS2)
   
    print("Listening")


def on_message(client, userdata, message):
    global buzz
    global watering
    global value
    global thresholds
    global low_threshold
    global high_threshold
    thresholds = get_threshold()
    low_threshold = thresholds[0]
    high_threshold = thresholds[1]
    print("Received message " + str(message.payload.decode('utf-8')))
    print(f"Threshold levels: ",thresholds)
    if str(message.payload.decode('utf-8')) == 'Water plant':
        watering = True
        
    elif str(message.payload.decode('utf-8')) == 'Swipe':
        watering = False
        
    else:
        value = float(str(message.payload.decode('utf-8')))

    if (watering == True) & (value < low_threshold):
        buzz = True 
    elif (buzz == True) & (value < high_threshold):
        pass
    else:
        buzz = False
        watering = False
        

class Service:
    """
    Here is a good documentation about the concepts in ble;
    https://learn.adafruit.com/introduction-to-bluetooth-low-energy/gatt

    In TI SensorTag there is a control characteristic and a data characteristic which define a service or sensor
    like the Light Sensor, Humidity Sensor etc

    Please take a look at the official TI user guide as well at
    https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide
    """

    def __init__(self):
        self.data_uuid = None
        self.ctrl_uuid = None

class LEDAndBuzzer(Service):
    """
        Adapted from various sources. Src: https://evothings.com/forum/viewtopic.php?t=1514 and the original TI spec
        from https://processors.wiki.ti.com/index.php/CC2650_SensorTag_User's_Guide#Activating_IO

        Codes:
            1 = red
            2 = green
            3 = red + green
            4 = buzzer
            5 = red + buzzer
            6 = green + buzzer
            7 = all
    """

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa65-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa66-0451-4000-b000-000000000000"

    async def notify(self, client, code):
        # enable the config
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # turn on the red led as stated from the list above using 0x01
        write_value = bytearray([code])
        await client.write_gatt_char(self.data_uuid, write_value)


async def run(address):
    
    async with BleakClient(address) as client:

        x = await client.is_connected()
        print("Connected: {0}".format(x))
        
        client1 = mqtt.Client()
        client1.on_connect = on_connect
        client1.on_message = on_message

        client1.username_pw_set(USERNAME, PASSWORD)
        client1.connect("18.142.17.12")
        client1.loop_start()
        
        led_and_buzzer = LEDAndBuzzer()
        
        while True:
            # we don't want to exit the "with" block initiating the client object as the connection is disconnected
            # unless the object is stored
            
            if buzz == True:  #TURN ON RED AND BUZZER
                await asyncio.sleep(0.5)
                await led_and_buzzer.notify(client, 0x05) 

            else: #ONLY TURN ON GREEN
                await asyncio.sleep(0.5)
                await led_and_buzzer.notify(client, 0x02) 
                
            
if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    import os
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "54:6C:0E:B7:B9:82"
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))
    loop.run_forever()
    