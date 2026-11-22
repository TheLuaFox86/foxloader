picoPC:
	cp -a src/. out
	cp -a boards/picoPC/. out
	lfrt lua make.lua

meowbit:
	cp -a src/. out
	cp -a boards/meowbit/. out
	lfrt lua make.lua

clean:
	rm -r out/*