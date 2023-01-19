#!/bin/sh

set -e

# Build
npm run build

# Package & Publish
cp package.json dist
cd dist
sed -i -E 's/dist\/index/index/' package.json
npm publish "$(npm pack)"
