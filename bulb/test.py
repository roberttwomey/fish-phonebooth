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
    
    await led.init_and_connect()
    print(f"connected to {thismac}")

    # await led.set_state(False) # off
    # time.sleep(1.5)
    # await led.set_state(True) # on
    # await led.set_brightness(0.25)
    # time.sleep(1.5)
    # await led.set_brightness(0.1)

    # for i in range(5):
    #     for b in np.linspace(0.0, 1.0, 30):
    #         await led.set_brightness(b)

    #     for b in np.linspace(1.0, 0.0, 30):
    #         await led.set_brightness(b)

    # for b in np.linspace(1.0, 0.0, 6):
    #     await led.set_brightness(b)
    #     time.sleep(5)

    # color set
    await led.set_color_bar('orangered')
    await led.set_brightness(0.25)
    time.sleep(1.5)
    await led.set_color_bar('violet')
    time.sleep(1.5)
    await led.set_color_bar('cyan')
    time.sleep(3.0)

    # warm/cool white
    await led.set_brightness(1.0)
    print("testing warm/cool white")
    await led.set_color_white_bar(-1.0)
    time.sleep(1.5)
    await led.set_color_white_bar(1.0)
    time.sleep(1.5)
    await led.set_color_white_bar(0)
    time.sleep(1.5)

    time.sleep(2)


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()