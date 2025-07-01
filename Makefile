DOCKER=docker

WUNDERK_IMAGE=wunderk
WUNDERK_VERSION=latest
WUNDERK_CTR=wunderk

WUNDERK_HOME=$(shell pwd)
DATAVOL=$(WUNDERK_HOME)/.data
SRCDIR=$(WUNDERK_HOME)

all: $(WUNDERK_IMAGE)

.PHONY: all

$(WUNDERK_IMAGE):
	$(DOCKER) build -t $(WUNDERK_IMAGE) -f Dockerfile .

run: $(DATAVOL)
	$(DOCKER) run -tid -p 9701:9701 -p 9702:9702 \
		-v $(DATAVOL):/app/data -v ./wui:/app/wui \
		--name $(WUNDERK_CTR) $(WUNDERK_IMAGE)

$(DATAVOL):
	mkdir -p $(DATAVOL)
	mkdir -p $(DATAVOL)/models

stop:
	$(DOCKER) stop $(WUNDERK_CTR)
	$(DOCKER) rm $(WUNDERK_CTR)

shell:
	$(DOCKER) exec -ti $(WUNDERK_CTR) /bin/bash

logs:
	$(DOCKER) logs $(WUNDERK_CTR) -f

rmi:
	$(DOCKER) rmi $(WUNDERK_IMAGE):$(WUNDERK_VERSION)
	$(DOCKER) system prune -f
clean:
	rm -rf $(DATAVOL)

# Publish to the registry at Github
publish:
	@docker tag $(WUNDERK_IMAGE):$(WUNDERK_VERSION) ghcr.io/xenocloud/$(WUNDERK_IMAGE):$(WUNDERK_VERSION)
	@docker push ghcr.io/xenocloud/$(WUNDERK_IMAGE):$(WUNDERK_VERSION)

test:
	- ./test.sh 
