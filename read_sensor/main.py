# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import os
import asyncio
import platform
import struct
from client import setup, send_data

from aioconsole import ainput
from bleak import BleakClient

NAME = "TNG"
DURATION = 20
ADDRESS = "54:6C:0E:B7:82:82"
username = "aegis"
password = "aegis2021"

GESTURE_DELAY = 1


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
        self.period_uuid = None

    async def read(self, client):
        raise NotImplementedError()


class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def enable(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)
        write_value = bytearray([0x0A]) # check the sensor period applicable values in the sensor tag guide mentioned above
        await client.write_gatt_char(self.period_uuid, write_value)

        return self

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)



class BatteryService(Service):
    def __init__(self):
        super().__init__()
        self.data_uuid = "00002a19-0000-1000-8000-00x805f9b34fb"

    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return int(val[0])
        
        
class MovementSensorMPU9250SubService:

    def __init__(self):
        self.bits = 0

    def enable_bits(self):
        return self.bits

    def cb_sensor(self, data):
        raise NotImplementedError
        

class MovementSensorMPU9250(Sensor):
    GYRO_XYZ = 7
    ACCEL_XYZ = 7 << 3
    MAG_XYZ = 1 << 6
    ACCEL_RANGE_2G  = 0 << 8
    ACCEL_RANGE_4G  = 1 << 8
    ACCEL_RANGE_8G  = 2 << 8
    ACCEL_RANGE_16G = 3 << 8

    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa81-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa82-0451-4000-b000-000000000000"
        self.ctrlBits = 0

        self.sub_callbacks = []

    def register(self, cls_obj: MovementSensorMPU9250SubService):
        self.ctrlBits |= cls_obj.enable_bits()
        self.sub_callbacks.append(cls_obj.cb_sensor)

    async def start_listener(self, client, *args):
        # start the sensor on the device
        await client.write_gatt_char(self.ctrl_uuid, struct.pack("<H", self.ctrlBits))

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)

    def callback(self, sender: int, data: bytearray):
        list_of_data = {}
        unpacked_data = struct.unpack("<hhhhhhhhh", data)
        for cb in self.sub_callbacks:
            data = cb(unpacked_data)
            list_of_data.update(data)
        return list_of_data


class AccelerometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.ACCEL_XYZ | MovementSensorMPU9250.ACCEL_RANGE_4G
        self.scale = 8.0/32768.0 # TODO: why not 4.0, as documented? @Ashwin Need to verify

    def cb_sensor(self, data):
        '''Returns (x_accel, y_accel, z_accel) in units of g'''
        rawVals = data[3:6]
        #print("[MovementSensor] Accelerometer:", tuple([ v*self.scale for v in rawVals ]))
        data = tuple([ v*self.scale for v in rawVals ])
        return {"acc": data}



class GyroscopeSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.GYRO_XYZ
        self.scale = 500.0/65536.0

    def cb_sensor(self, data):
        '''Returns (x_gyro, y_gyro, z_gyro) in units of degrees/sec'''
        rawVals = data[0:3]
        #print("[MovementSensor] Gyroscope:", tuple([ v*self.scale for v in rawVals ]))
        data = tuple([ v*self.scale for v in rawVals ])
        return {"gyro": data}

def unpack(data):
    acc_data = data["acc"]
    gyro_data = data["gyro"]
    return acc_data + gyro_data


async def run(address):
    
    mqtt_server = setup()
    
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected to Bluetooth: {0}".format(x))
        
        
        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()


        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)

        await movement_sensor.start_listener(client)
        print("Get ready...")

        while True:
            await asyncio.sleep(GESTURE_DELAY)
            print("Start!!!")

            list_of_data = []
    
            for i in range(DURATION):
                await asyncio.sleep(0.05)  # slightly less than 100ms to accommodate time to print results
                data = await movement_sensor.read(client)
                data_to_add = unpack(data)
                data_to_add = data_to_add[0:6]
                list_of_data.append(data_to_add)

            print("Recording ended")

            send_data(mqtt_server, list_of_data)
            
            userinput = await ainput("Continue? (Enter to input gesture, any to exit)")
            if userinput != "":
                exit(0)
            else:
                print(f"Get ready for next gesture...\n")
    
    
if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        ADDRESS
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )
   
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))

