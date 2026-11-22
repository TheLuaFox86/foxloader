import rando
from foxloader_api import *
global __BOOT
__BOOT = {
    "name": "FoxLoader",
    "path": '/',
    "osName": "FoxLoader"
}
def bootConf(name="UnkownOS"):
    __BOOT["osName"] = name

def Status(text="...", stat=None, fr=""):
            a = fr
            if fr == "":
                a = __BOOT.get("name") or "?" 

            print("Status: [" + a + "]: " + text)
            if not stat == None:
                stat.text = text
def Main():
    gc.collect()
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
        global title
        title = label.Label(terminalio.FONT, text="FoxLoader CPY V0", color=0xFFFFFF)
        title.x = 1
        title.y = 10

        #create the status label
        global status
        status = label.Label(terminalio.FONT, text="Loading...", color=0x000000)
        status.x = 1
        status.y = 33

        main_group.append(title)
        main_group.append(status)

        display.root_group = main_group

        display.refresh()


        
        

        print("FoxLoader Has Started")
        Status("checking for on board input", status)
        hasLocalInput = False
        if flcfg.get("input"):
            inp = flcfg["input"]
            if inp["type"] == 0: # CardKB
                hasLocalInput = True

            elif inp["type"] == 1: # pins (primaraly used for buttons)
                hasLocalInput = True

        Status("looking for boot device(s)", status)
        bootables = []
        for v in flcfg["bootables"]:
            if v in mounted_filesystems:
                if "FL-CPY_EFI" in os.listdir(flcfg["filesystems"][v]["mnt"]):
                    if "_BOOT_.py" in os.listdir(flcfg["filesystems"][v]["mnt"] + "/FL-CPY_EFI"):
                        bootables.append({
                            "name": v,
                            "mnt": flcfg["filesystems"][v]["mnt"],
                            "osName": "UnkownOS"
                        })

        def execfile(path):
            data = ""
            with open(path, "r") as f:
                data = f.read()

            return exec(data)
        
        def boot(name=flcfg["bootables"][0]):
            for v in bootables:
                if v["name"] == name:
                    reason = "Halted"
                    try:
                        global __BOOT
                        __BOOT.update(v)
                        os.chdir(__BOOT["mnt"])
                        execfile("FL-CPY_EFI/_BOOT_.py")
                    except Exception as e:
                        reason = "Errored: " + str(e)
                    
                    time.sleep(2)
                    title.text = __BOOT["osName"] + " " + reason
                    print(title.text)
                    status.text = ""
                    display.refresh()

        if len(bootables) < 1:
            Status("No Bootable Mediam Found", status)
        elif len(bootables) == 1:
            Status("Booting Into " + bootables[0]["name"])
            boot(bootables[0]["name"])
            Status(fr="FoxLoader", text="Rebooting", stat=status)
            display.refresh()
            del fb_bitmap, fb_palette, main_group, title, status
            gc.collect()
            Main()

        print("Loading BootMenu")
        i = 0
        once = True
        while True:
            time.sleep(0.1)
            if hasLocalInput:
                a = "boot From: " + bootables[i]["name"]
                if not status.text == a:
                    status.text = a
                    display.refresh()
                    
            elif not hasLocalInput and once:
                Status(text-"Oh No Were Stuck!", fr="FoxLoader", stat=status)
                display.refresh()

            key = flinput()
            if key == "UP":
                print(i, bootables)
                i = i + 1
                try:
                    a = bootables[i]
                except:
                    i = 0
                
            if key == "OK":
                boot(bootables[i]["name"])
            
            
Main()