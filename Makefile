BUILD_FOLDER := _build
SNAPSHOTS_FOLDER := __SNAPSHOTS__
SMARTPY_CLI_PATH := $(BUILD_FOLDER)/smartpy-cli
PYTHONPATH := $(SMARTPY_CLI_PATH):$(shell pwd)
FLEXTESA_IMAGE=oxheadalpha/flextesa:latest
FLEXTESA_SCRIPT=kathmandubox
CONTAINER_NAME=ibc-tezos-sandbox
LIGO_VERSION=0.57.0

HAS_DOCKER := $(shell which docker)

LIGO_COMPILATIONS := $(wildcard contracts/tezos/ligo/*.mligo)
SMARTPY_COMPILATIONS := $(filter-out %/__init__.py, $(wildcard compilation/**/*.py)) $(wildcard compilation/**/**/*.py)
SMARTPY_TESTS := $(filter-out %/__init__.py, $(wildcard test/**/*.py)) $(wildcard test/**/**/*.py)
LIGO_TESTS := $(wildcard test/tezos/ligo/*.mligo) $(wildcard test/tezos/ligo/**/*.mligo)

touch_done=@mkdir -p $(@D) && touch $@;

all: install-dependencies

##
## + Compilations
##
$(SNAPSHOTS_FOLDER)/compilation/tezos/ligo:
	@mkdir -p $(SNAPSHOTS_FOLDER)/compilation/tezos/ligo

contracts/%: contracts/%.mligo
ifeq (, ${HAS_DOCKER})
	@echo "Skipping compilation $<, it requires docker."
else
	@./ligo compile contract $< --output-file $(SNAPSHOTS_FOLDER)/compilation/$*_contract.tz
#@docker run --rm -v "$(PWD)":"$(PWD)" -w "$(PWD)" ligolang/ligo:$(LIGO_VERSION) compile contract $< --output-file $(SNAPSHOTS_FOLDER)/compilation/$*_contract.tz
endif

compilation/%: compilation/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh compile $< $(SNAPSHOTS_FOLDER)/compilation/$* --erase-comments

clean-tezos-compilations:
	@rm -rf $(SNAPSHOTS_FOLDER)/compilation/tezos

clean-evm-compilations:
	@rm -rf $(SNAPSHOTS_FOLDER)/compilation/evm

compile-tezos: clean-tezos-compilations $(SNAPSHOTS_FOLDER)/compilation/tezos/ligo $(LIGO_COMPILATIONS:%.mligo=%) $(SMARTPY_COMPILATIONS:%.py=%) setup_env
	@find $(SNAPSHOTS_FOLDER)/compilation/ -name "*_contract.tz" -exec sed -i -E 's/#.*//' {} \; -exec wc -c {} \; | sort > $(SNAPSHOTS_FOLDER)/compilation/tezos/sizes.txt
	@cat $(SNAPSHOTS_FOLDER)/compilation/tezos/sizes.txt

compile-evm: setup_env clean-evm-compilations
	@npm run compile

compile: compile-tezos compile-evm
	@echo "Compiled all contracts."
##
## - Compilations
##

##
## + Tests
##
test/%: test/%.py install-dependencies
	@$(SMARTPY_CLI_PATH)/SmartPy.sh test $< $(SNAPSHOTS_FOLDER)/test/$* --html

test/tezos/ligo/%: test/tezos/ligo/%.mligo
ifeq (, ${HAS_DOCKER})
	@echo "Skipping compilation $<, it requires docker."
else
	@./ligo run test $<
#@docker run --rm -v "$(PWD)":"$(PWD)" -w "$(PWD)" ligolang/ligo:$(LIGO_VERSION) compile contract $< --output-file $(SNAPSHOTS_FOLDER)/compilation/$*_contract.tz
endif

clean-tezos-tests:
	@rm -rf $(SNAPSHOTS_FOLDER)/test/tezos

clean-evm-tests:
	@rm -rf $(SNAPSHOTS_FOLDER)/test/evm

test-tezos: clean-tezos-tests $(SMARTPY_TESTS:%.py=%) $(LIGO_TESTS:%.mligo=%) setup_env

test-evm: setup_env clean-evm-tests
	@npm run test

test: test-tezos test-evm
	@echo "Tested all contracts."

test-sdk: install-npm-packages
	@yarn test:sdk

##
## - Tests
##

##
## + Deployment
##

export CONFIG_PATH ?= deployment/tezos/configs/ghostnet.yaml
deploy-tezos: setup_env
	@python3 deployment/tezos/apply.py $(SNAPSHOTS_FOLDER)/deployment-$(notdir $(basename $(CONFIG_PATH))).yaml

export INFURA_URL ?= https://ropsten.infura.io/v3/75829a5785c844bc9c9e6e891130ee6f
deploy-evm: setup_env
	@npm run deploy 2>&1 | tee __SNAPSHOTS__/evm-deployment.txt

deploy: deploy-evm deploy-tezos

deploy-docs:
	./scripts/update-docs.sh

##
## - Deployment
##

fmt-check:
	python3 -m black --check .
	yarn lint:check
	yarn prettier:check

fmt-fix:
	python3 -m black .
	yarn lint:fix
	yarn prettier:fix

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
	@yarn
	@yarn build
	$(touch_done)

install-pip-packages: $(BUILD_FOLDER)/pip-packages
$(BUILD_FOLDER)/pip-packages: requirements.txt
	@pip install -r requirements.txt --quiet
	$(touch_done)

install-dependencies: install-smartpy install-npm-packages install-pip-packages
##
## - Install dependencies
##
