import rando
from foxloader_api import *


go = input2(prompt="Goto Repl? (N/y): ", timeout=10)

print("FoxLoader is starting...")
if go == "Y" or go == "y":
    # Exit the user program cleanly so CircuitPython enters the REPL.
    raise SystemExit
else:
    #from afafruit_bitmap_font import bitmap_font
    dspc = flcfg["display"]
    fb_bitmap = displayio.Bitmap(dspc["width"], dspc["height"], dspc["depth"])
    fb_palette = displayio.Palette(dspc["depth"])
    fb_palette[0] = 0x0000FF  # Bright blue test color

    main_group = displayio.Group()

    main_group.append(displayio.TileGrid(fb_bitmap, pixel_shader=fb_palette))

    
 
    # Create the Title Label
    title = label.Label(terminalio.FONT, text="FoxLoader CPY V0", color=0xFFFFFF)
    title.x = 1
    title.y = 10

    #create the status label
    status = label.Label(terminalio.FONT, text="Loading...", color=0x000000)
    status.x = 1
    status.y = 33

    main_group.append(title)
    main_group.append(status)

    display.root_group = main_group

    display.refresh()


    global __BOOT

    __BOOT = {
        "name": "FoxLoader",
        "path": '/'
    }
    
    def Status(text="...", fr=""):
        a = fr
        if fr == "":
           a = __BOOT.get("name") or "?" 

        print("Status: [" + a + "]: " + text)
        status.text = text

    print("FoxLoader Has Started")
    Status("checking for on board input")
    hasLocalInput = False
    if flcfg.get("input"):
        inp = flcfg["input"]
        if inp["type"] == 0: # CardKB
            print("cardKB is not supported yet")

        elif inp["type"] == 1: # pins (primaraly used for buttons)
            hasLocalInput = True

    Status("looking for a boot device")
    bootables = []
    for v in flcfg["bootables"]:
        if v in flcfg["bootables"]:
            if v in mounted_filesystems:
                if "FL-CPY_EFI" in os.listdir(flcfg["filesystems"][v]["mnt"]):
                    if "_BOOT_.py" in os.listdir(flcfg["filesystems"][v]["mnt"] + "/FL-CPY_EFI"):
                        bootables.append({
                            "name": v,
                            "path": flcfg["filesystems"][v]["mnt"]
                        })

    def execfile(path):
        data = ""
        with open(path, "r") as f:
            data = f.read()

        exec(data)

    
    def boot(name=flcfg["bootables"][0]):
        for v in bootables:
            if v["name"] == name:
                __BOOT = v
                os.chdir(__BOOT["path"])
                execfile("FL-CPY_EFI/_BOOT_.py")

   
    if len(bootables) < 1:
        Status("No Bootable Mediam Found")
    elif len(bootables) == 1:
        Status("Booting Into " + bootables[0]["name"])
        boot(bootables[0]["name"])

    while True:
        time.sleep(0.1)
        if hasLocalInput:
            print("found")

        display.refresh
