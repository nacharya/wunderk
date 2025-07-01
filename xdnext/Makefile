XDNEXT_BIN=xdnext

XDNEXT_HOME=$(shell pwd)
DATAVOL=$(HOME)/.data
SRCDIR=$(XDNEXT_HOME)

all: $(XDNEXT_BIN)

.PHONY: all

$(XDNEXT_BIN):
	go build -o $(XDNEXT_BIN)

run: $(DATAVOL)
	export XDNEXT_HOME="~/.config/xdnext/config.json"
	$(XDNEXT_HOME)/$(XDNEXT_BIN) server start	

init: $(DATAVOL)
	export XDNEXT_HOME="~/.config/xdnext/config.json"
	$(XDNEXT_HOME)/$(XDNEXT_BIN) init

test: $(DATAVOL)
	export XDNEXT_HOME="~/.config/xdnext/config.json"
	$(XDNEXT_HOME)/$(XDNEXT_BIN) test show
	$(XDNEXT_HOME)/$(XDNEXT_BIN) test user
	$(XDNEXT_HOME)/$(XDNEXT_BIN) test realm
	$(XDNEXT_HOME)/$(XDNEXT_BIN) test task
	$(XDNEXT_HOME)/$(XDNEXT_BIN) test show

$(DATAVOL):
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

reset:
	rm -rf $(DATAVOL)
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

stop:
	- ps aux | grep $(XDNEXT_BIN) | grep -v grep | awk '{print $$2}' | xargs kill -9

shell:
	$(DOCKER) exec -ti $(VSXAPI_CTR) /bin/bash

logs:
	tail -f xdn.log

clean:
	rm $(XDNEXT_BIN)
	rm -rf $(DATAVOL)
	rm *.log

