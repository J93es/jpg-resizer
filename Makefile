PYTHON = python
SCRIPT = jpg_resizer.py
IMG_DIR = ./images
YEAR = $(shell date +%Y)

.PHONY: all default run help clean

all: default

default: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 200 1200 1200

j93es: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 200 1200 1200 true "ⓒ $(YEAR). j93es. All rights reserved."

run: $(SCRIPT)
	$(PYTHON) $(SCRIPT) $(kb) $(max_width) $(max_height) $(use_meta_watermark) $(watermark)

help:
	@echo "사용법:"
	@echo "    make"
	@echo "    make default"
	@echo "    Usage: make run {target image size (kb)} {max image width(pixel)} {max image height(pixel)} {true | false(optional: default=false)} {watermark text(optional: default='')}"
	@echo "    Example: make run 200 1200 1200 true 'ⓒ 2021. j93es. All rights reserved.'"
	@echo "    make clean"

clean:
	rm -f *.pyc
	rm -f ./images/*
	touch ./images/.gitkeep
	rm -rf ./resized_images
	mkdir -p $(IMG_DIR)