PYTHON = python
SCRIPT = jpg_resizer.py
IMG_DIR = ./images
YEAR = $(shell date +%Y)

.PHONY: all default run help clean

all: default

default: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 200 1200 1200

j93es: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 200 1200 1200 "ⓒ $(YEAR). j93es. All rights reserved."

run: $(SCRIPT)
	$(PYTHON) $(SCRIPT) $(kb) $(max_width) $(max_height) $(watermark)

help:
	@echo "사용법:"
	@echo "    make"
	@echo "    make default"
	@echo "    make run kb={target image size per kb} max_width={max image width pixel} max_height={max image height pixel} watermark={watermark text(optional)}"
	@echo "    make clean"

clean:
	rm -f *.pyc
	rm -f ./images/*
	touch ./images/.gitkeep
	rm -rf ./resized_images
	mkdir -p $(IMG_DIR)