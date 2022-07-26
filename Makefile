BUILD_FOLDER := _build
SNAPSHOTS_FOLDER := __SNAPSHOTS__
SMARTPY_CLI_PATH := $(BUILD_FOLDER)/smartpy-cli
PYTHONPATH := $(SMARTPY_CLI_PATH):$(shell pwd)
FLEXTESA_IMAGE=oxheadalpha/flextesa:latest
FLEXTESA_SCRIPT=jakartabox
CONTAINER_NAME=ibc-tezos-sandbox

COMPILATIONS := $(filter-out %/__init__.py, $(wildcard compilation/**/*.py))
TESTS := $(filter-out %/__init__.py, $(wildcard test/**/*.py))

touch_done=@mkdir -p $(@D) && touch $@;

all: install-dependencies

##
## + Compilations
##
compilation/%: compilation/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh compile $< $(SNAPSHOTS_FOLDER)/compilation/$* --erase-comments

clean_compilations:
	@rm -rf $(SNAPSHOTS_FOLDER)/compilation

compile-tezos: $(COMPILATIONS:%.py=%) setup_env
	@find $(SNAPSHOTS_FOLDER)/compilation/ -name "*_contract.tz" -exec sed -i 's/#.*//' {} \; -exec wc -c {} \; | sort -z > $(SNAPSHOTS_FOLDER)/compilation/sizes.txt
	@cat $(SNAPSHOTS_FOLDER)/compilation/sizes.txt

compile-evm: setup_env
	@npm run compile

compile: clean_compilations compile-tezos compile-evm
	@npm run compile
	@echo "Compiled all contracts."
##
## - Compilations
##

##
## + Tests
##
test/%: test/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh test $< $(SNAPSHOTS_FOLDER)/test/$* --html

clean_tests:
	@rm -rf $(SNAPSHOTS_FOLDER)/test

test-tezos: $(TESTS:%.py=%) setup_env

test-evm: setup_env
	@npm run test

test: clean_tests test-tezos test-evm
	@echo "Tested all contracts."
##
## - Tests
##

##
## + Deployment
##

export CONFIG_PATH ?= deployment/configs/ghostnet.yaml
deploy-tezos: setup_env
	@python3 deployment/apply.py $(SNAPSHOTS_FOLDER)/deployment-$(notdir $(basename $(CONFIG_PATH))).yaml

export INFURA_URL ?= https://ropsten.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f
deploy-evm: setup_env
	@npm run deploy > __SNAPSHOTS__/evm-deployment.txt

deploy: deploy-evm deploy-tezos
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
setup_env: install-dependencies

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

install-npm-packages: $(BUILD_FOLDER)/npm-packages
$(BUILD_FOLDER)/npm-packages: package.json
	@npm i --silent
	$(touch_done)

install-dependencies: install-smartpy install-npm-packages
	@pip install -r requirements.txt --quiet
##
## - Install dependencies
##
