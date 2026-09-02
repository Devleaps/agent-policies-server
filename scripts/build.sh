#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

GIT_SHA="${GIT_SHA:-$(git rev-parse HEAD)}"
VERSION="${VERSION:-dev}"
IMAGE_TAG="${IMAGE_TAG:-agent-policies-server:local}"

docker build \
	--build-arg GIT_SHA="$GIT_SHA" \
	--build-arg VERSION="$VERSION" \
	-t "$IMAGE_TAG" \
	.
