# -*- coding: utf-8 -*-
"""
TI CC2650 SensorTag
-------------------

Adapted by Ashwin from the following sources:
 - https://github.com/IanHarvey/bluepy/blob/a7f5db1a31dba50f77454e036b5ee05c3b7e2d6e/bluepy/sensortag.py
 - https://github.com/hbldh/bleak/blob/develop/examples/sensortag.py

"""
import asyncio
import platform
import struct

from client import setup, send_data
from bleak import BleakClient

ADDRESS = "54:6C:0E:B7:82:82"
TOPIC = "aegis/intensity"


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


class Sensor(Service):

    def callback(self, sender: int, data: bytearray):
        raise NotImplementedError()

    async def start_listener(self, client, *args):
        # start the sensor on the device
        write_value = bytearray([0x01])
        await client.write_gatt_char(self.ctrl_uuid, write_value)

        # listen using the handler
        await client.start_notify(self.data_uuid, self.callback)
    async def read(self, client):
        val = await client.read_gatt_char(self.data_uuid)
        return self.callback(1, val)


class IntensitySensor(Sensor):
    def __init__(self):
        super().__init__()
        self.data_uuid = "f000aa71-0451-4000-b000-000000000000"
        self.ctrl_uuid = "f000aa72-0451-4000-b000-000000000000"

    def callback(self, sender: int, data: bytearray):
        raw = struct.unpack('<h', data)[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        print("[IntensitySensor] Reading from light sensor:", 0.01 * (m << e))
        return 0.01 * (m << e)



async def run(address):

    mqtt_server = setup()
    async with BleakClient(address) as client:
        x = await client.is_connected()
        print("Connected: {0}".format(x))

        intensity_sensor = IntensitySensor()
        await intensity_sensor.start_listener(client)

        while True:
            data = await intensity_sensor.read(client)
            send_data(mqtt_server, data, TOPIC)
            await asyncio.sleep(5)
    


if __name__ == "__main__":
    """
    To find the address, once your sensor tag is blinking the green led after pressing the button, run the discover.py
    file which was provided as an example from bleak to identify the sensor tag device
    """

    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    address = (
        "54:6C:0E:B7:82:82"
        if platform.system() != "Darwin"
        else "6FFBA6AE-0802-4D92-B1CD-041BE4B4FEB9"
    )
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(address))
    loop.run_forever()