WUI_BIN=wui.py

WUI_HOME=$(shell pwd)
DATAVOL=$(HOME)/.data
SRCDIR=$(WUI_HOME)

all: run

.PHONY: all

run: $(DATAVOL)
	uv run $(WUI_HOME)/wui.py

init: $(DATAVOL)
	uv run $(WUI_HOME)/$(WUI_BIN) init

ruff:
	ruff check $(WUI_HOME)/$(WUI_BIN)
	ruff check $(WUI_HOME)/$(WUI_BIN) --fix
	ruff check $(WUI_HOME)/$(WUI_BIN) --fix --exit-zero


test: $(DATAVOL)
	export WUI_HOME="~/.config/xdnext/config.json"
	$(WUI_HOME)/$(WUI_BIN) test show
	$(WUI_HOME)/$(WUI_BIN) test user
	$(WUI_HOME)/$(WUI_BIN) test realm
	$(WUI_HOME)/$(WUI_BIN) test task
	$(WUI_HOME)/$(WUI_BIN) test show

$(DATAVOL):
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

reset:
	rm -rf $(DATAVOL)
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

stop:
	- ps aux | grep $(WUI_BIN) | grep -v grep | awk '{print $$2}' | xargs kill -9

shell:
	$(DOCKER) exec -ti $(VSXAPI_CTR) /bin/bash

logs:
	tail -f xdn.log

clean:
	rm $(WUI_BIN)
	rm -rf $(DATAVOL)
	rm *.log

