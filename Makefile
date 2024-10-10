PYTHON = python

SCRIPT = jpg_resizer.py

IMG_DIR = ./images

.PHONY: all default run help clean

all: default

default: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 50 900 900

run: $(SCRIPT)
	$(PYTHON) $(SCRIPT) $(kb) $(w_pixel)

help:
	@echo "사용법:"
	@echo "    make"
	@echo "    make default"
	@echo "    make run kb={target image size per kb} max_width={max image width pixel} max_heught={max image height pixel}"
	@echo "    make clean"

clean:
	rm -f *.pyc
	rm -f ./images/*
	rm -rf ./resized_images
	rm -rf ./tmp
	mkdir -p $(IMG_DIR)