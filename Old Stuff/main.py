#config
background = (13, 13, 76)
wdir = ""
debugmode = 1
filesystems = ["/flash", "/sd"]
#code
from meowbit import *
screen.sync = 0
import os
import math
import time
screen.fill(0)
screen.loadBmp("logo.bmp", -1, -1)
screen.text("FoxLoader", 8, 0, 2, 255)
screen.text("MPY", 56, 8)
screen.text("By TheLuaFox86", 0, 120)
screen.refresh()
buzzer.melody("c6:1 f6:2", 120)
time.sleep_ms(1000)


if wdir == "":
	print("operating in root")
else:
	os.chdir(wdir)
	print("operating in " + wdir)


dl = os.listdir()
selected = 0
fss = 0
count = 0
pg = 1
def option(txt, y):
	if selected == count:
		screen.text(txt, 0, y,  1, 80)
		return 1
	else:
		screen.text(txt, 0, y)
		return 0
go = 1
while go:
	if selected > len(dl) :
		selected = 0
	
	if selected < 0:
		selected = len(dl)
		
	pg = math.floor(selected / 4) + 1
	calc = pg * 4
	if debugmode:
		print("Selected: ", selected)
	try:
		screen.fill(background)
		screen.text(str(filesystems[fss]), 0, 8)
		screen.text("SDmenu", 0, 0)
		count = 0
		y = 20
		if sensor.btnValue("down"):
			selected = selected + 1
	
		if sensor.btnValue("up"):
			selected = selected - 1
			
		if sensor.btnValue("b"):
			os.chdir("..")
			dl = os.listdir()
			
		if selected <= -1:
			selected = 0
	
		if option("...", y):
			if sensor.btnValue("a"):
				os.chdir("..")
				dl = os.listdir()
	
		screen.text("(/\),(\/) to scroll", 0, 81)
		screen.text("(A) folder (B) Back", 0, 89)
		screen.text("(<) boot (>) FS", 0, 97)
		for d in dl:
			count =  count + 1
			if count <= calc:
				if count >= calc - 4:
					y = y + 11
					if option(d, y):
						if sensor.btnValue("a"):
							os.chdir(d)
							dl = os.listdir()
					
						if sensor.btnValue("left"):
							try:
								go = 0
								screen.fill(0)
								screen.sync = 1
								execfile("_BOOT_.py")
							except:
								screen.sync = 0
								go = 1
								screen.fill(0)
								screen.text("fail")
								screen.refresh()
								buzzer.melody("a3:2 r a3:2", 120)
			
			
						if sensor.btnValue("right"):
							try:
								if fss == len(filesystems) - 1:
									os.chdir(list(filesystems)[0])
									fss = 0
								else:
									os.chdir(filesystems[fss + 1])
									fss = fss + 1

							except:
								screen.sync = 0
								go = 1
								screen.fill(0)
								screen.text("sdcard not detected")
								screen.text("try rebooting", 0, 8)
								screen.refresh()
								buzzer.melody("a3:2 r a3:2", 120)
								time.sleep_ms(3000)
			
			
				
		screen.refresh()
		time.sleep_ms(5)
	except:
		os.chdir("..")
		dl = os.listdir()
