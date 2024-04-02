import time
from govee_btled_windows import BluetoothLED
import asyncio

async def main():
    # Replace this with your LED's MAC address
    led = BluetoothLED('74209773-2F79-D43E-5EE9-AEF071CEA34C')
    await led.init_and_connect()
    print("connected")

    # OCEAN DESCENT
    # colors https://www.w3.org/TR/css-color-3/#svg-color
    await led.set_brightness(1.0)
    await led.set_color('cyan')
    time.sleep(1.5)
    await led.set_color('blue')
    time.sleep(1.5)
    await led.set_color('darkblue')
    time.sleep(1.5)
    await led.set_color('navy')
    time.sleep(1.5)
    await led.set_color('midnightblue')
    await led.set_brightness(0.1)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()