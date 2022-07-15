BUILD_FOLDER := _build
SNAPSHOTS_FOLDER := __SNAPSHOTS__
SMARTPY_CLI_PATH := $(BUILD_FOLDER)/smartpy-cli
PYTHONPATH := $(SMARTPY_CLI_PATH):$(shell pwd)
FLEXTESA_IMAGE=oxheadalpha/flextesa:latest
FLEXTESA_SCRIPT=jakartabox
CONTAINER_NAME=ibc-tezos-sandbox

COMPILATIONS := $(filter-out %/__init__.py, $(wildcard compilations/*.py))
TESTS := $(filter-out %/__init__.py, $(wildcard tests/*.py))

touch_done=@mkdir -p $(@D) && touch $@;

all: install-dependencies

##
## + Compilations
##
compilations/%: compilations/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh compile $< $(SNAPSHOTS_FOLDER)/compilation/$* --erase-comments

clean_compilations:
	@rm -rf $(SNAPSHOTS_FOLDER)/compilation

compile: clean_compilations $(COMPILATIONS:%.py=%) setup_env
	@echo "Compiled all contracts."
##
## - Compilations
##

##
## + Tests
##
tests/%: tests/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh test $< $(SNAPSHOTS_FOLDER)/test/$* --html

clean_tests:
	@rm -rf $(SNAPSHOTS_FOLDER)/test

test: clean_tests $(TESTS:%.py=%) setup_env
	@echo "Tested all contracts."
##
## - Tests
##

##
## + Deployment
##
export CONFIG_PATH ?= deployment/configs/ghostnet.yaml
deploy: install-dependencies
	@python3 deployment/apply.py $(SNAPSHOTS_FOLDER)/deployment-$(notdir $(basename $(CONFIG_PATH))).yaml
##
## + Deployment
##

fmt-check:
	python3 -m black --check .

fmt-fix:
	python3 -m black .

start-sandbox:
	@docker run -v $(shell pwd):$(shell pwd) --rm --name "$(CONTAINER_NAME)" --detach \
		-p 20000:20000 \
		-e block_time=1 \
		"$(FLEXTESA_IMAGE)" "$(FLEXTESA_SCRIPT)" start

stop-sandbox:
	@docker stop "$(CONTAINER_NAME)"

export PYTHONPATH
setup_env: # Setup environment variables

clean:
	@rm -rf $(BUILD_FOLDER)

##
## + Install Dependencies
##
install-smartpy: $(BUILD_FOLDER)/install-smartpy
$(BUILD_FOLDER)/install-smartpy:
	@rm -rf $(SMARTPY_CLI_PATH)
	@bash -c "bash <(curl -s https://smartpy.io/cli/install.sh) --prefix $(SMARTPY_CLI_PATH) --yes"
	$(touch_done)

install-dependencies: install-smartpy
	@pip install -r requirements.txt --quiet
##
## - Install dependencies
##
