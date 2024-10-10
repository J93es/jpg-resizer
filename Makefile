PYTHON = python

SCRIPT = jpg_resizer.py

IMG_DIR = ./images

.PHONY: all default run help clean

all: default

default: $(SCRIPT)
	$(PYTHON) $(SCRIPT) 200 1200 1200

run: $(SCRIPT)
	$(PYTHON) $(SCRIPT) $(kb) $(max_width) $(max_height)

help:
	@echo "사용법:"
	@echo "    make"
	@echo "    make default"
	@echo "    make run kb={target image size per kb} max_width={max image width pixel} max_height={max image height pixel}"
	@echo "    make clean"

clean:
	rm -f *.pyc
	rm -f ./images/*
	rm -rf ./resized_images
	rm -rf ./tmp
	mkdir -p $(IMG_DIR)