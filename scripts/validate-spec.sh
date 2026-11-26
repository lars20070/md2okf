#!/usr/bin/env bash

# Build every Docker Sandbox kit (kits/<kit>/md2okf-<kit>.yaml, with the
# md2okf-<kit>.dockerfile recipe beside it) and check the built artifact with
# kit-tck, the Sandbox Kit conformance suite.
#
# Why a build: these are schema v3 source kits, and `sbx kit validate` cannot
# read one ("has no kit builder configured"). The kit frontend named in each
# descriptor's `# syntax=` line validates the descriptor before it builds
# anything, then kit-tck judges what actually came out: annotations, layers,
# staged sources, image config and overlay ownership.
#
# What it cannot see: composition. Each kit is checked alone, so a clash
# between a mixin and the workload it lands on -- a file, a credential, a
# network grant -- only shows in a live sandbox (`make test-sandbox`).
#
# Kits are discovered, not listed, so a kit being authored is checked from its
# first commit -- long before md2okf.agents registers it. Every registered kit
# (one pyproject.toml force-include line per registered agent) must also be
# present, so a lost kit fails here rather than validating nothing.
#
# Needs Docker with Buildx and kit-tck, but no sbx and no login. A cold build
# pulls the kit frontend and every base image, so it is not an offline check.
# Environment:
#   KIT_PLATFORMS  platforms to build (default: linux/amd64,linux/arm64). A
#                  foreign architecture needs QEMU or a native builder node;
#                  set it to your own platform for a quick local run.
#   KIT_BUILDER    the Buildx builder (default: md2okf-kits, created as a
#                  docker-container builder if missing, because exporting an
#                  OCI layout needs one).

set -euo pipefail

KIT_TCK_VERSION=3.0.0-m.12

# Resolve the repo root from this script's location so it works from any CWD.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"
platforms="${KIT_PLATFORMS:-linux/amd64,linux/arm64}"
builder="${KIT_BUILDER:-md2okf-kits}"

required="$(<"${repo_root}/SBX_VERSION")"
if [[ ! "${required}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo "Error: SBX_VERSION must contain exactly one X.Y.Z version." >&2
	exit 1
fi

# The sbx floor still applies wherever sbx is installed: it is what builds and
# runs these kits for users, and CI installs exactly that release. Validation
# itself does not use it.
if command -v sbx >/dev/null 2>&1; then
	installed="$(sbx version | grep -m1 -oE '[0-9]+\.[0-9]+\.[0-9]+')" || {
		echo "Error: could not read a version from 'sbx version'." >&2
		exit 1
	}
	if [[ "$(printf '%s\n' "${required}" "${installed}" | sort -V | head -n1)" != "${required}" ]]; then
		echo "Error: sbx ${required} or newer is required; found ${installed}." >&2
		echo "Please upgrade sbx with Homebrew or APT." >&2
		exit 1
	fi
else
	echo "Note: sbx is not installed; skipping the sbx ${required} floor check."
fi

if ! docker buildx version >/dev/null 2>&1; then
	echo "Error: 'docker buildx' is not available. Install Docker with Buildx." >&2
	exit 1
fi
if ! command -v kit-tck >/dev/null 2>&1; then
	echo "Error: 'kit-tck' not found in PATH. Install ${KIT_TCK_VERSION} from" >&2
	echo "https://github.com/docker/sandbox-kit-spec/releases/tag/v${KIT_TCK_VERSION}" >&2
	exit 1
fi
if ! kit-tck version | grep -qF "${KIT_TCK_VERSION}"; then
	echo "Error: kit-tck ${KIT_TCK_VERSION} is required (the spec sbx ${required} bundles); found:" >&2
	kit-tck version >&2
	exit 1
fi

if ! docker buildx inspect "${builder}" >/dev/null 2>&1; then
	echo "Creating the Buildx builder ${builder} (docker-container driver)..."
	docker buildx create --name "${builder}" --driver docker-container --bootstrap >/dev/null
fi

layouts="$(mktemp -d)"
trap 'rm -rf "${layouts}"' EXIT

status=0

# Every registered kit must exist; md2okf.agents registers an agent only once
# pyproject.toml bundles its kit.
registered="$(sed -nE 's|^"kits/([a-z0-9-]+)" = "md2okf/kits/[a-z0-9-]+"$|\1|p' "${repo_root}/pyproject.toml")"
if [[ -z "${registered}" ]]; then
	echo "Error: no registered kits found in pyproject.toml's force-include." >&2
	exit 1
fi
for kit in ${registered}; do
	if [[ ! -f "${repo_root}/kits/${kit}/md2okf-${kit}.yaml" ]]; then
		echo "Error: registered kit kits/${kit}/md2okf-${kit}.yaml is missing." >&2
		status=1
	fi
done

found=0
for kit_dir in "${repo_root}"/kits/*/; do
	kit_dir="${kit_dir%/}"
	kit="$(basename "${kit_dir}")"
	stem="md2okf-${kit}"
	if [[ -f "${kit_dir}/spec.yaml" ]]; then
		echo "Error: kits/${kit}/spec.yaml is a v2 spec; kits are schema v3 (${stem}.yaml)." >&2
		status=1
	fi
	if [[ ! -f "${kit_dir}/${stem}.yaml" ]]; then
		echo "Error: kits/${kit}/ has no ${stem}.yaml descriptor." >&2
		status=1
		continue
	fi
	found=$((found + 1))
	layout="${layouts}/${kit}"
	echo "Building kits/${kit} for ${platforms} with ${builder}..."
	# Keep going after a failure, so one run reports every invalid kit.
	if ! docker buildx build \
		--builder "${builder}" \
		--platform "${platforms}" \
		--provenance=mode=max,version=v1 \
		-f "${kit_dir}/${stem}.yaml" \
		--output "type=oci,dest=${layout},tar=false,name=${stem}:latest" \
		"${kit_dir}"; then
		echo "Error: kits/${kit} did not build." >&2
		status=1
		continue
	fi
	echo "Checking kits/${kit} with kit-tck ${KIT_TCK_VERSION}..."
	kit-tck validate --layout "${layout}" latest || status=1

	# kit-tck checks /home and /home/agent. An overlay lands on a filesystem
	# it has never seen, so every other entry must belong to root or the
	# agent too: a uid that rode in from a release tarball may be a real
	# account on the base. Mixins only; a workload's layers are its base's.
	if grep -qx 'kind: mixin' "${kit_dir}/${stem}.yaml"; then
		owners="$(
			for blob in "${layout}"/blobs/sha256/*; do
				tar --numeric-owner -tvf "${blob}" 2>/dev/null || true
			done | awk '{print ($2 ~ /\//) ? $2 : $3 "/" $4}' | sort -u
		)"
		foreign="$(grep -vxE '0/0|1000/1000' <<<"${owners}" || true)"
		if [[ -n "${foreign}" ]]; then
			echo "Error: kits/${kit} ships entries owned by ${foreign//$'\n'/, }." >&2
			status=1
		else
			echo "kits/${kit}: every overlay entry belongs to root or the agent."
		fi
	fi
done

if [[ "${found}" -eq 0 ]]; then
	echo "Error: no kits/*/md2okf-*.yaml found under ${repo_root}." >&2
	exit 1
fi
exit "${status}"
