
# BLE Bulb Demo

This folder contains a standalone demo for scanning, testing, and controlling Govee BLE bulbs using Python.

## Prerequisites

You need Python 3 and the following libraries:

```bash
pip install bleak colour
```

## Structure

- `govee_btled/`: Library for communicating with Govee devices.
- `scan.py`: Script to scan for nearby BLE devices.
- `test_connection.py`: Script to test basic connection to a device.
- `control_bulb.py`: Script to control Govee bulb functions (color, brightness, etc.).

## Usage

### 1. Scan for Devices

Identify your bulb's MAC address. It might show up as "Govee", "Minger", or similar.

```bash
python scan.py
# Or filter by name
python scan.py --filter govee
```

### 2. Test Connection

Verify that you can connect to the device.

```bash
python test_connection.py <MAC_ADDRESS>
```

Example: `python test_connection.py 74209773-2F79-D43E-5EE9-AEF071CEA34C`

### 3. Control Bulb

Run the full demo sequence (On -> Off -> Brightness -> Colors -> White Temp).

```bash
python control_bulb.py --mac <MAC_ADDRESS>
```

Example: `python control_bulb.py --mac 74209773-2F79-D43E-5EE9-AEF071CEA34C`

You can also edit `control_bulb.py` to change the default MAC address.

## Troubleshooting

- **Device not found**: Ensure Bluetooth is enabled and the device is powered on.
- **Connection failed**: Move closer to the device. BLE has limited range.
- **Permission Denied**: On macOS, you might need to grant Bluetooth permissions to your terminal or IDE. On Linux, ensure you have proper permissions (e.g., run as root or add user to `bluetooth` group).
