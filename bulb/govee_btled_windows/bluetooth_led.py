from enum import IntEnum
from colour import Color
from bleak import BleakClient
import bleak

import asyncio

from .shades_of_white import values as SHADES_OF_WHITE

UUID_CONTROL_CHARACTERISTIC = '00010203-0405-0607-0809-0a0b0c0d2b11'

def color2rgb(color):
    """ Converts a color-convertible into 3-tuple of 0-255 valued ints. """
    col = Color(color)
    rgb = col.red, col.green, col.blue
    rgb = [round(x * 255) for x in rgb]
    return tuple(rgb)


class LedCommand(IntEnum):
    """ A control command packet's type. """
    POWER = 0x01
    BRIGHTNESS = 0x04
    COLOR = 0x05


class LedMode(IntEnum):
    """
    The mode in which a color change happens in.

    Currently only manual is supported.
    """
    MANUAL = 0x02
    MICROPHONE = 0x06
    SCENES = 0x05
    RGBBAR = 0x15
    RGB = 0x0d


class BluetoothLED:
    def __init__(self, mac, timeout=5):
        self.mac = mac
        # self._bt = BleakClient(mac, backend=bleak.backends.corebluetooth, timeout=timeout)
        self._bt = BleakClient(mac, timeout=timeout)
        self.init_and_connect()

    async def init_and_connect(self):
        await self._bt.connect()
        # print(self._bt.is_connected)
        # print(self._bt.services.characteristics)

    def __del__(self):
        self._cleanup()

    # There seem to be some issues revolving around disconnecting from BLE objects using Bleak.
    # https://github.com/hbldh/bleak/issues/133
    # https://stackoverflow.com/questions/39599252/windows-ble-uwp-disconnect
    # Though, removing the resources for the connection should do the trick.
    def _cleanup(self):
        self._bt = None

    async def set_state(self, onoff):
        """ Controls the power state of the LED. """
        return await self._send(LedCommand.POWER, [0x1 if onoff else 0x0])

    async def set_brightness(self, value, debug=False):
        """
        Sets the LED's brightness.

        `value` must be a value between 0.0 and 1.0
        """
        # invalue = float(value)
        if not 0 <= float(value) <= 1:
            raise ValueError(f'Brightness out of range: {value}')
        # value = round(value * 0xFF)
        value = round(value * 100)
        if debug:
            print(f"brightness {invalue} {value}")
        return await self._send(LedCommand.BRIGHTNESS, [value])
    
    async def set_color(self, color):
        """
        Sets the LED's color.

        `color` must be a color-convertible (see the `colour` library),
        e.g. 'red', '#ff0000', etc.
        """
        thisdata = color2rgb(color)
        # print(f"set color: {thisdata}") # debug
        return await self._send(LedCommand.COLOR, [LedMode.RGB, *color2rgb(color)])


    async def set_color_bar(self, color, debug=False):
        """
        Sets the LED's color.

        `color` must be a color-convertible (see the `colour` library),
        e.g. 'red', '#ff0000', etc.
        """
        thisdata = color2rgb(color)
        if debug:
            print(f"set color: {thisdata}") # debug
        return await self._send(LedCommand.COLOR, [LedMode.RGBBAR, 0x01, *color2rgb(color),
                                                   0x00, 0x00, 0x00, 0x00, 0x00,
                                                   0xff, 0x0f])


    async def set_color_white(self, value):
        """
        Sets the LED's color in white-mode.

        `value` must be a value between -1.0 and 1.0
        White mode seems to enable a different set of LEDs within the bulb.
        This method uses the hardcoded RGB values of whites, directly taken from
        the mechanism used in Govee's app.
        """
        if not -1 <= value <= 1:
            raise ValueError(f'White value out of range: {value}')
        value = (value + 1) / 2  # in [0.0, 1.0]
        index = round(value * (len(SHADES_OF_WHITE) - 1))
        white = Color(SHADES_OF_WHITE[index])

        # two = value*0x07de
        # 2000 0x07d0
        # 9000 0x2328
        two = round((value * 7000) + 2000)
        # twohex = hex(two)
        valA = int(two/256)
        valA = f"{valA:#0{4}x}"
        valB = hex(two%256)
        # print(valA, valB)
        # Set the color to white (although ignored) and the boolean flag to True
        # return await self._send(LedCommand.COLOR, [LedMode.MANUAL, 0xff, 0xff, 0xff, 0x01, *color2rgb(white)])
        # return await self._send(LedCommand.COLOR, [LedMode.RGB, 0xff, 0xff, 0xff, 0x23, 0x28, *color2rgb(white)])
        return await self._send(LedCommand.COLOR, [LedMode.RGB, 0xff, 0xff, 0xff, 
                                                   eval(valA), eval(valB),
                                                   *color2rgb(white)])

    async def set_color_white_bar(self, value):
        """
        Sets the LED's color in white-mode.

        `value` must be a value between -1.0 and 1.0
        White mode seems to enable a different set of LEDs within the bulb.
        This method uses the hardcoded RGB values of whites, directly taken from
        the mechanism used in Govee's app.
        """
        if not -1 <= value <= 1:
            raise ValueError(f'White value out of range: {value}')
        value = (value + 1) / 2  # in [0.0, 1.0]
        index = round(value * (len(SHADES_OF_WHITE) - 1))
        white = Color(SHADES_OF_WHITE[index])

        # two = value*0x07de
        # 2000 0x07d0
        # 9000 0x2328
        two = round((value * 7000) + 2000)
        # twohex = hex(two)
        valA = int(two/256)
        valA = f"{valA:#0{4}x}"
        valB = hex(two%256)
        # print(valA, valB)
        
        # Set the color to white (although ignored) and the boolean flag to True
        # return await self._send(LedCommand.COLOR, [LedMode.MANUAL, 0xff, 0xff, 0xff, 0x01, *color2rgb(white)])
        # return await self._send(LedCommand.COLOR, [LedMode.RGB, 0xff, 0xff, 0xff, 0x23, 0x28, *color2rgb(white)])
        return await self._send(LedCommand.COLOR, [LedMode.RGBBAR, 0x01, 0xff, 0xff, 0xff, 
                                                   eval(valA), eval(valB),
                                                   *color2rgb(white), 0xff, 0x0f])
    
    # async def set_scene(self, value):
    #     """
    #     Sets LED into a preprogrammed scene.
    #     """
    #     return await self._send(LedCommand.COLOR, [0x04, value])


    async def _send(self, cmd, payload, debug=False):
        """ Sends a command and handles payload padding. """
        if not isinstance(cmd, int):
            raise ValueError('Invalid command')
        if not isinstance(payload, bytes) and not (
                isinstance(payload, list) and all(isinstance(x, int) for x in payload)):
            raise ValueError('Invalid payload')
        if len(payload) > 17:
            raise ValueError('Payload too long')

        cmd = cmd & 0xFF
        payload = bytes(payload)

        frame = bytes([0x33, cmd]) + bytes(payload)

        # print(f"front 4 {frame}")
        # pad frame data to 19 bytes (plus checksum)
        frame += bytes([0] * (19 - len(frame)))

        # The checksum is calculated by XORing all data bytes
        checksum = 0
        for b in frame:
            checksum ^= b

        frame += bytes([checksum & 0xFF])

        # debug
        if debug:
            for b in frame:
                print(f"{b:02x}", end=" ")
            print()

        # return frame

        async def main():
            await self._bt.write_gatt_char(UUID_CONTROL_CHARACTERISTIC, frame)

        await main()

        # self._dev.char_write(UUID_CONTROL_CHARACTERISTIC, frame)
        # Implement Bleak's BLE functionality here. This replaces the original implementation's use of pyGATT, which is not
        # supported on most Windows Bluetooth interfaces or devices.
