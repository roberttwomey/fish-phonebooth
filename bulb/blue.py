import time
from govee_btled_windows import BluetoothLED
import asyncio
import numpy as np

bulb = '74209773-2F79-D43E-5EE9-AEF071CEA34C'
lightbar1 = '44ADBA7B-66E7-F108-D84B-2C4C87504092'
lightbar2 = 'B845E65A-83D0-D7DF-EA68-5B0CA817B783'
darkTime = 385
startTime = 145

async def main():
    # time.sleep(startTime)
    # Replace this with your LED's MAC address
    thismac = lightbar1
    # thismac = lightbar1
    led = BluetoothLED(thismac)
    led2 = BluetoothLED(lightbar2)
    # # led = BluetoothLED(thismac)
    # if await led.init_and_connect():
    #     print("connected {thismac}")

    # if await led2.init_and_connect():
    #     print("connected {lightbar2}")

    # # await led.set_state(False) # off
    # # time.sleep(1.5)
    # # await led.set_state(True) # on
    # # await led.set_brightness(0.25)
    # # time.sleep(1.5)
    # # await led.set_brightness(1.0)

    # # for i in range(5):
    # #     for b in np.linspace(0.0, 1.0, 30):
    # #         await led.set_brightness(b)

    # #     for b in np.linspace(1.0, 0.0, 30):
    # #         await led.set_brightness(b)

    # # for b in np.linspace(1.0, 0.0, 6):
    # #     await led.set_brightness(b)
    # #     time.sleep(2)

    # # await led.set_brightness(1.0)
    # # await led.set_color('orangered')

    # # await led.test_bar()
    # # await led._send(0x09, [0x0c, 0x2a, 0x01, 0x02, 0x01, 0xf9])
    # # await led._send(0x05, [0x15, 0x05, 0x03, 0x55])
    # # await led._send(0x05, [0x15, 0x05, 0x03, 0x64])
    # # await led._send(0x05, [0x15, 0x05, 0x03, 0x01])
    # # await led._send(0x05, [0x15, 0x05, 0x03, 0x64])
    # # await led._send(0x05, [0x15, 0x01, 0x00, 0x00, 0xff, 0x00, 0x00, 0x00, 0x00, 0x00, 0xff, 0x0f])

    # # OCEAN DESCENT
    # # colors https://www.w3.org/TR/css-color-3/#svg-color
    # # time.sleep(5)

    # await led.set_brightness(0.5)
    # await led2.set_brightness(0.5)
    # await led.set_color_bar('blue')
    # await led2.set_color_bar('blue')
    # b = 0.5
    
    # # Go Down
    # while b > 0.01:
    #     await led.set_brightness(b)
    #     await led2.set_brightness(b)
    #     time.sleep(0.63)
    #     b -= 0.01

    # # Go Black
    # await led.set_brightness(0)
    # await led2.set_brightness(0)
    # await led.set_color_bar('black')
    # await led2.set_color_bar('black')

    # # Wait on Black
    # time.sleep(darkTime)
    b = 0.01

    if await led.init_and_connect():
        print("connected {thismac}")

    if await led2.init_and_connect():
        print("connected {lightbar2}")
    
    # Go Blue Again
    await led.set_brightness(0.50)
    await led2.set_brightness(0.50)
    await led.set_color_bar('blue')
    await led2.set_color_bar('blue')
    print("fully reset and changed back to blue lights")


    #Reid Test 1
    # await led.set_brightness(0.5)
    # await led2.set_brightness(0.5)
    # # await led.set_color_bar('white')
    # # await led2.set_color_bar('white')
    # # time.sleep(5)
    # await led.set_color_bar('blue')
    # await led2.set_color_bar('blue')

    # time.sleep(3)
    # await led.set_brightness(0.25)
    # await led2.set_brightness(0.25)

    # time.sleep(3)
    # await led.set_brightness(0.1)
    # await led2.set_brightness(0.1)

    # time.sleep(3)
    # await led.set_brightness(0)
    # await led2.set_brightness(0)
    # await led.set_color_bar('black')
    # await led2.set_color_bar('black')

    # time.sleep(5)
    
    # await led.set_brightness(0)
    # await led2.set_brightness(0)
    # await led.set_color_bar('blue')
    # await led2.set_color_bar('blue')
    # time.sleep(5)
    # await led.set_brightness(0.1)
    # await led2.set_brightness(0.1)
    # time.sleep(3)
    # await led.set_brightness(0.25)
    # await led2.set_brightness(0.25)
    # time.sleep(3)
    # await led.set_brightness(0.5)
    # await led2.set_brightness(0.5)


    # time.sleep(3)
    # await led.set_color_bar('blue')
    # await led2.set_color_bar('blue')
    # time.sleep(3)
    # await led.set_color_bar('darkblue')
    # await led2.set_color_bar('darkblue')
    # time.sleep(3)
    # await led.set_color_bar('navy')
    # await led2.set_color_bar('navy')
    # time.sleep(3)
    # await led.set_color_bar('midnightblue')
    # await led2.set_color_bar('midnightblue')
    # # await led.set_brightness(0.1)
    # time.sleep(3)
    # await led.set_color_bar('black')
    # await led2.set_color_bar('black')
    
    # time.sleep(3)
    
    # await led.set_color_bar('midnightblue')
    # await led2.set_color_bar('midnightblue')
    # time.sleep(3)
    # await led.set_color_bar('navy')
    # await led2.set_color_bar('navy')
    # time.sleep(3)
    # await led.set_color_bar('blue')
    # await led2.set_color_bar('blue')
    # time.sleep(3)
    # await led.set_color_bar('cyan')
    # await led2.set_color_bar('cyan')


    # time.sleep(5)
    # await led.set_color_bar('white')
    # await led2.set_color_bar('white')

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