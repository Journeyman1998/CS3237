# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import datetime
import platform
import struct
import time
import math

from aioconsole import ainput
from bleak import BleakClient

NAME = "TNG"
DURATION = 20
ADDRESS = "54:6C:0E:B7:82:82"
FIRST_GESTURE_DELAY = 2
NEXT_GESTURE_DELAY = 2


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


class OpticalSensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa71-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa72-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa73-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        tt = datetime.datetime.now()
        raw = struct.unpack('<h', data)[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        # print(f"[OpticalSensor @ {tt}] Reading from light sensor: {0.01 * (m << e)}")
        return 0.01 * (m << e)


class HumiditySensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa21-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa22-0451-4000-b000-000000000000"
        self.period_uuid = "f000aa23-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        (rawT, rawH) = struct.unpack('<HH', data)
        temp = -40.0 + 165.0 * (rawT / 65536.0)
        RH = 100.0 * (rawH / 65536.0)
        return temp, RH


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


class MagnetometerSensorMovementSensorMPU9250(MovementSensorMPU9250SubService):
    def __init__(self):
        super().__init__()
        self.bits = MovementSensorMPU9250.MAG_XYZ
        self.scale = 4912.0 / 32760
        # Reference: MPU-9250 register map v1.4

    def cb_sensor(self, data):
        '''Returns (x_mag, y_mag, z_mag) in units of uT'''
        rawVals = data[6:9]
        #print("[MovementSensor] Magnetometer:", tuple([ v*self.scale for v in rawVals ]))
        data = tuple([ v*self.scale for v in rawVals ])
        return {"mag": data}


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
    

async def run(address, data_id_file):
    
    counter = 0
    
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        #light_sensor = await OpticalSensor().enable(client)
        #humidity_sensor = await HumiditySensor().enable(client)
        #battery = BatteryService()

        #prev_batter_reading_time = time.time()
        #batter_reading = await battery.read(client)
        #print("Battery Reading", batter_reading)
        
        
        acc_sensor = AccelerometerSensorMovementSensorMPU9250()
        gyro_sensor = GyroscopeSensorMovementSensorMPU9250()

        movement_sensor = MovementSensorMPU9250()
        movement_sensor.register(acc_sensor)
        movement_sensor.register(gyro_sensor)
        await movement_sensor.start_listener(client)
        
        print("Get ready for recording")
        await asyncio.sleep(FIRST_GESTURE_DELAY)
        
        while True:
            print("Recording started")
            list_of_data = []
            
            for i in range(DURATION):
                # set according to your period in the sensors; otherwise sensor will return same value for all the readings
                # till the sensor refreshes as defined in the period
                await asyncio.sleep(0.05)  # slightly less than 100ms to accommodate time to print results
                data = await movement_sensor.read(client)
                data_to_add = unpack(data)
                list_of_data.append(data_to_add)
                
                #if time.time() - prev_batter_reading_time > 15 * 60:  # 15 mins
                #    batter_reading = await battery.read(client)
                #    print("Battery Reading", batter_reading)
                #    prev_batter_reading_time = time.time()
            
            print("Recording ended")
           
            
            data_id = write_id(data_id_file)
            data_filename = f"data_{NAME}_{data_id}.csv"
            data_file = os.path.join(data_dir, data_filename)
            data = clean_data(list_of_data)
            
            write_data(data_file, data)
            
            userinput = await ainput("Continue? (Enter to continue, any to exit)")
            if userinput != "":
                exit(0)
            else:
                print(f"Get ready for next gesture {data_id+1}\n")
                await asyncio.sleep(NEXT_GESTURE_DELAY)

def all_zeroes(data):
    for d in data:
        if not math.isclose(d, 0.0):
            return False
    return True
    
def write_id(data_id_file):
    if(not os.path.isfile(data_id_file)):
        with open(data_id_file, "w+") as f:
            f.write("1")
        data_id = 0
    else:
        with open(data_id_file, "r+") as f:
            data_id = int(f.read().strip())
            f.seek(0)
            f.write(str(data_id + 1))
    return data_id
    
# some data cleaning
# remove the starting 0s (there is a lag bet the movement and the reading of values. The readings are read before the user is signalled to move)
def clean_data(data):

    for i in range(len(data)):
        if not all_zeroes(data[i]):
            start = i
            break
    
    for j in range(len(data)-1, start, -1):
        if not all_zeroes(data[j]):
            end = j
            break
    
    return data[start:end+1]
    
    
def write_data(data_file, data):
    with open(data_file, 'w+', newline = '') as f:
        writer = csv.writer(f, delimiter=',')
        
        writer.writerow(header)
        for i in range(len(data)):
            writer.writerow(data[i])
    
if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """
    
    header = ["acc_x","acc_y","acc_z","gyro_x","gyro_y","gyro_z","mag_x","mag_y","mag_z"]

    import os
    import csv

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        ADDRESS #"54:6c:0e:b5:56:00"
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )

    data_dir = "./cc2650_data"
    data_id_filename = "data_id.txt"
    data_id_file = os.path.join(data_dir, data_id_filename)

    if(not os.path.isdir(data_dir)):
        os.mkdir(data_dir)
   
    

    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address, data_id_file))
    
