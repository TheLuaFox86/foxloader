#foxloader api
import board
import time
time.sleep(1)
import random
from adafruit_display_text import label
import terminalio
import supervisor
import busio
import json
import os
import displayio
from fourwire import FourWire
import time
import usb_cdc

print("FoxLoader API: starting")


def input2(prompt="", timeout=0):
    print(prompt, end="")
    serial = usb_cdc.console
    start_time = time.monotonic()
    buffer = ""
    if timeout > 0:
        while (time.monotonic() - start_time) < timeout:
            if serial.in_waiting > 0:
                char = serial.read(1).decode("utf-8", "ignore")
                
                # Handle Enter/Return
                if char in ("\r", "\n"):
                    print()  # Move to next line
                    return buffer
                
                # Handle Backspace / Delete
                elif char in ("\b", "\x7f"):
                    if len(buffer) > 0:
                        buffer = buffer[:-1]
                        print("\b \b", end="")  # Erase character on terminal
                
                # Echo and store normal characters
                else:
                    buffer += char
                    print(char, end="")
                    
            time.sleep(0.01)  # Small delay to prevent CPU hogging

        print()  # Newline after timeout
        return None
    else:
        return input(prompt)

with open("/flcfg.json") as f:
    flcfg = json.load(f)


import storage
print("FoxLoader API: Initializing SPI Buses")
spi = {}
for SPIID in ["SPI0", "SPI1", "SPI2"]:
    if SPIID in flcfg:
        if flcfg[SPIID].get('MOSI'):
            spi[SPIID] = busio.SPI(clock=getattr(board, flcfg[SPIID]["CLK"]), MOSI=getattr(board, flcfg[SPIID]["MOSI"]), MISO=getattr(board, flcfg[SPIID]["MISO"]))
        elif flcfg[SPIID].get("MODE"):
            a = flcfg[SPIID]["MODE"]
            if a["type"] == "func":
                spi[SPIID] = getattr(board, a["index"])()
            elif a["type"] == "direct":
                spi[SPIID] =  getattr(board, a["index"])

        while not spi[SPIID].try_lock():
            pass

        if flcfg[SPIID].get('baudrate'):
            spi[SPIID].configure(baudrate=flcfg[SPIID]['baudrate'])

        spi[SPIID].unlock()

displayio.release_displays()

i2c = {}
for I2CID in ["I2C-0", "I2C-1", "I2C-2"]:
    if I2CID in flcfg:
        if flcfg[I2CID].get('SCL'):
            i2c[I2CID] = busio.I2C(getattr(board, flcfg[I2CID]["SCL"]), getattr(board, flcfg[I2CID]["SDA"]), frequency=flcfg[I2CID]["freq"])
        elif flcfg[I2CID].get("MODE"):
            a = flcfg[I2CID]["MODE"]
            if a["type"] == "func":
                i2c[I2CID] = getattr(board, a["index"])()
            elif a["type"] == "direct":
                i2c[I2CID] =  getattr(board, a["index"])



mounted_filesystems = set()
for name, fs in flcfg['filesystems'].items():
    print("FoxLoader API: Loading Filesystem: " + name + " with type: " + str(fs["type"]))
    if fs["type"] == 0:
        mounted_filesystems.add(name)
    if fs["type"] == 1:
        try:
            import sdcardio
            sd = sdcardio.SDCard(spi[fs["SPI"]], getattr(board, fs["CS"]))
            if sd is ...:
                raise RuntimeError(f"SD card init failed (CS={fs['CS']})")
            vfs = storage.VfsFat(sd)
            storage.mount(vfs, fs["mnt"])
            mounted_filesystems.add(name)
        except Exception as err:
            print("FoxLoader API: failed to mount " + name + ". Error: " + str(err))

    elif fs["type"] == 2:
        try:
            vfs = storage.VfsFat(getattr(board, fs["index"]))
            storage.mount(vfs, fs["mnt"])
            mounted_filesystems.add(name)
        except Exception as err:
            print("FoxLoader API: failed to mount " + name + ". Error: " + str(err))

# init display
print("FoxLoader API: loading display driver")
print("")
if flcfg['display']["driver"] == "ST7789":
    from adafruit_st7789 import ST7789

    tft_cs = getattr(board, flcfg['display']['CS'])
    tft_dc = getattr(board, flcfg['display']['DC'])
    tft_rst = getattr(board, flcfg['display']['RST'])

    display_bus = FourWire(
        spi[flcfg['display']['SPI']],
        command=tft_dc,
        chip_select=tft_cs,
        reset=tft_rst,
    )

    display = ST7789(
        display_bus,
        width=flcfg['display']['width'],
        height=flcfg['display']['height'],
        rowstart=flcfg['display']['rowstart'],
        auto_refresh=flcfg['display']['auto_refresh'],
    )

elif hasattr(board, 'DISPLAY') and board.DISPLAY is not None:
    print("FoxLoader API: found internal display")
    display = board.DISPLAY

else:
    print("FoxLoader API: driver for display NOT FOUND")

print("FoxLoader API: loading input driver")
if flcfg.get("input"):
    a = flcfg["input"]
    if a["type"] == 0: # CardKB
        print("FoxLoader API: input found as CardKB")
        from cardkb import CardKB
        global flinput
        ckb = CardKB(i2c[a["bus"]])
        def flinput(raw=False):
            if raw:
                return ckb
            
            result = ckb.read_key()
            
            if result is None or result[0] is None:
                return None
            
            keycode, character, modifier = result
            print(keycode)
            if keycode == 0x0D:
                return "OK"
            elif keycode == 0x1B:
                return "BACK"
            elif ckb.is_arrow(keycode):
                # Map arrow keycodes to strings
                arrows = {0xB4: "LEFT", 0xB5: "UP", 0xB6: "DOWN", 0xB7: "RIGHT",
                        0x98: "LEFT", 0x99: "UP", 0xA4: "DOWN", 0xA5: "RIGHT"}
                return arrows.get(keycode, "")
            return None   
    else:
        def flinput(raw=False):
            return None

import gc

    

print("FoxLoader API: Done!")