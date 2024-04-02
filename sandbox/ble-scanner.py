import asyncio
from bleak import BleakScanner

async def discover_devices():
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device: {device.name}, Address: {device.address}")


# # asyncio.run(discover_devices())
        
# async def adv_data():
#     devicedata = await BleakScanner(cb: use_bdaddr).discover()
#     for device in devicedata: 
#         print(f"Device: {device}")

asyncio.run(discover_devices())
# asyncio.run(adv_data())
