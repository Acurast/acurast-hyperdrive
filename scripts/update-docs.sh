#!/bin/bash

# Clean up

rm -rf apps/documentation/build
rm -rf packages/ibcf-sdk/api_documentation

# Build documentation
npm --prefix apps/documentation install
npm --prefix apps/documentation run build
yarn workspace ibcf-sdk run generate:doc

# Deploy
rm -rf /tmp/docs
git clone --depth 1 --branch gh-pages git@github.com:airgap-it/ibcf.git "/tmp/docs"
git -C /tmp/docs rm -rf .
cp -r apps/documentation/build/* /tmp/docs
cp -r packages/ibcf-sdk/api_documentation /tmp/docs/api
git -C /tmp/docs add .
git -C /tmp/docs commit --amend --no-edit
git -C /tmp/docs push --force origin gh-pages
