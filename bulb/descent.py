import time
from govee_btled_windows import BluetoothLED
import asyncio
import numpy as np

bulb = '74209773-2F79-D43E-5EE9-AEF071CEA34C'
lightbar1 = 'EA5D5E0C-AD67-8D3D-2ABE-501A97DA4077'
lightbar2 = '46A48234-B7BF-80C1-8A7F-F66A3FA977B5'

async def main():
    # Replace this with your LED's MAC address
    thismac = lightbar1
    led = BluetoothLED(thismac)
    if await led.init_and_connect():
        print("connected {thismac}")
    
    # await led.set_state(False) # off
    # time.sleep(1.5)
    # await led.set_state(True) # on
    # await led.set_brightness(0.25)
    # time.sleep(1.5)
    # await led.set_brightness(1.0)

    # for i in range(5):
    #     for b in np.linspace(0.0, 1.0, 30):
    #         await led.set_brightness(b)

    #     for b in np.linspace(1.0, 0.0, 30):
    #         await led.set_brightness(b)

    # for b in np.linspace(1.0, 0.0, 6):
    #     await led.set_brightness(b)
    #     time.sleep(2)

    # await led.set_brightness(1.0)
    # await led.set_color('orangered')

    # await led.test_bar()
    # await led._send(0x09, [0x0c, 0x2a, 0x01, 0x02, 0x01, 0xf9])
    # await led._send(0x05, [0x15, 0x05, 0x03, 0x55])
    # await led._send(0x05, [0x15, 0x05, 0x03, 0x64])
    # await led._send(0x05, [0x15, 0x05, 0x03, 0x01])
    # await led._send(0x05, [0x15, 0x05, 0x03, 0x64])
    # await led._send(0x05, [0x15, 0x01, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x0f])

    # OCEAN DESCENT
    # colors https://www.w3.org/TR/css-color-3/#svg-color
    await led.set_brightness(0.5)
    await led.set_color_bar('white')
    time.sleep(3)
    await led.set_color_bar('cyan')
    time.sleep(3)
    await led.set_color_bar('blue')
    time.sleep(3)
    await led.set_color_bar('darkblue')
    time.sleep(3)
    await led.set_color_bar('navy')
    time.sleep(3)
    await led.set_color_bar('midnightblue')
    # await led.set_brightness(0.1)
    time.sleep(3)
    await led.set_color_bar('black')
    

    # await led.set_color_white(-1.0)
    # time.sleep(1.5)
    # await led.set_color_white(1.0)
    # time.sleep(1.5)
    # await led.set_color_white(0)

    time.sleep(2)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()