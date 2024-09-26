from govee_btled_windows import BluetoothLED
import time
import asyncio

async def main():
    # Replace this with your LED's MAC address
    # led = BluetoothLED('XX:XX:XX:XX:XX:XX')
    led = BluetoothLED('74209773-2F79-D43E-5EE9-AEF071CEA34C')
    await led.init_and_connect()
    await led.set_state(True)
    await led.set_color_white(-.55)
    time.sleep(.5)
    await led.set_color('orangered')
    await led.set_brightness(.7)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.close()

# Or comment all that out and uncomment this if you want to do a search for MAC addresses:
# print(my_funcs.search_btle("minger"))
# print(my_funcs.search_btle("govee"))
