PRODUCT=$(shell basename `dirname $(PWD)`)
SOFTWARE_HOME=/usr/lib/zope/lib/python
INSTANCE_HOME=/var/lib/zope
ZOPECTL=$(INSTANCE_HOME)/bin/zopectl

all: test zcheck

test:
	$(ZOPECTL) test -m Products.$(PRODUCT)

zcheck:
	python zcheck.py

help:
	@$(ZOPECTL) test --help

env:
	@echo $(PRODUCT)
