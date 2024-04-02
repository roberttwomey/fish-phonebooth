# uses Bleak to search for BTLE devices
# takes 'device_of_interest' string
# scans thru BTLE devices to find devices that match device of interest.
# e.g. Govee lights that use "Minger" moniker in Bluetooth device name.

def search_btle(device_of_interest):
    import asyncio
    from bleak import BleakScanner

    found_devices = []
    device_of_interest = "govee"

    async def main():
        devices = await BleakScanner().discover()
        for d in devices:
            split_BLEDevice = (str(d).split(": "))
            # print(split_BLEDevice[1].lower())
            if device_of_interest in split_BLEDevice[1].lower():
                found_devices.append({"address": split_BLEDevice[0], "name":split_BLEDevice[1]})

    asyncio.run(main())
    return found_devices

if __name__ == '__main__':
    print(search_btle("minger"))