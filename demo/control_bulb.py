
import time
import asyncio
import argparse
import sys
from govee_btled import BluetoothLED
from colour import Color

# Default values - change these or pass as arguments
DEFAULT_MAC = '74209773-2F79-D43E-5EE9-AEF071CEA34C' 

async def main(mac_address):
    print(f"Connecting to {mac_address}...")
    led = BluetoothLED(mac_address)
    
    try:
        await led.init_and_connect()
        print("Connected!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        print("Ensure the device is powered on and within range.")
        return

    try:
        print("Turning OFF...")
        await led.set_state(False)
        time.sleep(1.5)

        print("Turning ON...")
        await led.set_state(True)
        time.sleep(1.5)
        
        print("Setting Brightness to 25%...")
        await led.set_brightness(0.25)
        time.sleep(1.5)
        
        print("Setting Brightness to 100%...")
        await led.set_brightness(1.0)
        time.sleep(1.5)
        
        colors = ['orangered', 'violet', 'cyan']
        for color in colors:
            print(f"Setting Color: {color}...")
            await led.set_color_bar(color)
            time.sleep(1.5)
            
        print("Testing White Mode (Cool -> Warm)...")
        await led.set_color_white_bar(-1.0) # Coolest
        time.sleep(1.5)
        await led.set_color_white_bar(0.0)  # Neutral
        time.sleep(1.5)
        await led.set_color_white_bar(1.0)  # Warmest
        time.sleep(1.5)

        print("Demo complete.")
        
    except Exception as e:
        print(f"Error during operation: {e}")
    finally:
        # disconnect is handled by __del__ but we can be explicit if needed
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Control Govee BLE Bulb.")
    parser.add_argument("--mac", "-m", help="MAC address of the bulb", default=DEFAULT_MAC)
    args = parser.parse_args()
    
    # Windows workaround
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main(args.mac))
    finally:
        loop.close()
