
import asyncio
from bleak import BleakScanner
import argparse
import sys

# Windows workaround for occasional event loop issues
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def scan(filter_name=None):
    print("Scanning for BLE devices...")
    try:
        devices = await BleakScanner.discover()
    except Exception as e:
        print(f"Error during scan: {e}")
        return
    
    found = False
    print(f"{'Address':<40} {'Name':<30} {'RSSI'}")
    print("-" * 80)
    
    for d in devices:
        name = d.name or "Unknown"
        address = d.address
        rssi = d.rssi
        
        if filter_name:
            if filter_name.lower() in name.lower():
                print(f"{address:<40} {name:<30} {rssi}dBm")
                found = True
        else:
            print(f"{address:<40} {name:<30} {rssi}dBm")
            found = True
            
    if not found:
        if filter_name:
            print(f"No devices found matching '{filter_name}'")
        else:
            print("No devices found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan for BLE devices.")
    parser.add_argument("--filter", "-f", help="Filter devices by name (case-insensitive)", default=None)
    args = parser.parse_args()
    
    try:
        asyncio.run(scan(args.filter))
    except KeyboardInterrupt:
        print("\nScan interrupted by user.")
