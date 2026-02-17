
import asyncio
import sys
from bleak import BleakClient

async def test_connection(address):
    print(f"Attempting to connect to {address}...")
    try:
        async with BleakClient(address, timeout=10.0) as client:
            print(f"Connected: {client.is_connected}")
            
            # Read model number string if available (standard UUID 0x2A24)
            try:
                model_number = await client.read_gatt_char("00002a24-0000-1000-8000-00805f9b34fb")
                print(f"Model Number: {model_number.decode('utf-8')}")
            except Exception:
                print("Could not read Model Number characteristic.")

            print("Disconnecting...")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_connection.py <MAC_ADDRESS>")
        sys.exit(1)
        
    address = sys.argv[1]
    
    # Windows workaround
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(test_connection(address))
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
