#!/usr/bin/env bash
set -euo pipefail

# Open an interactive bash shell in the CONTAINERISED Pi runtime (Docker
# Compose) — for inspecting config, mounts, or the OKF output.
#
# Usage: bash-container.sh
#
# Self-contained: this driver shares no code with the sandbox driver. It
# overrides the image's `pi` entrypoint (see pi/container/Dockerfile) with bash
# and starts an ephemeral (`--rm`) container; all other config (security,
# resource limits, mounts, env) lives declaratively in pi/container/compose.yaml.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

compose_file="pi/container/compose.yaml"

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
	echo "Missing OPENROUTER_API_KEY environment variable." >&2
	exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
	echo "Docker CLI not found. Install Docker Desktop or Docker Engine and try again." >&2
	exit 1
fi

if ! docker info >/dev/null 2>&1; then
	echo "Docker does not appear to be running. Start Docker Desktop (or Docker Engine) and try again." >&2
	exit 1
fi

# Build the Pi agent image.
docker compose -f "${compose_file}" build

# Drop into an interactive shell (as the non-root runtime user, in /workspace).
docker compose -f "${compose_file}" run --rm -it --entrypoint bash pi
