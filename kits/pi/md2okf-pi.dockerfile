# Content recipe for md2okf-pi.yaml beside it. The result is a workload: the
# whole root filesystem Pi runs in.

# The pinned release binaries, downloaded and checksummed in a throwaway
# stage. Pinning the digests here, rather than reading each release's
# checksums file, means a re-uploaded asset fails the build too. The mq and
# okfctl half is identical in kits/claude and kits/codex.
FROM debian:trixie-slim AS fetch
ARG TARGETARCH
RUN apt-get update \
	&& apt-get install -y --no-install-recommends ca-certificates curl \
	&& rm -rf /var/lib/apt/lists/*
RUN <<'FETCH'
set -eu
case "${TARGETARCH}" in
amd64)
	mq_target=x86_64-unknown-linux-gnu
	mq_sha256=e60c2295845a3dfd5bf99b97cca9e8a268f80b6f4868907efac79f06420e32d1
	okfctl_sha256=938a9cf125c7f13945bc27132e420ca36f8fb95b1ce7b4cb907ec0fe70fcf3bc
	gms_asset=Linux_x86_64
	gms_sha256=95843162759da2c31dde082dd145be35db82164594796c294414b69790c2290e
	;;
arm64)
	mq_target=aarch64-unknown-linux-gnu
	mq_sha256=adc63fb3f1f01d3fe35f56deb5e09ab19f7f57142fcd7e2c8c0004fff6ed84c3
	okfctl_sha256=09821344881af75dde68476d3177363f915380ae43fea815b62b785109f7ec0a
	gms_asset=Linux_arm64
	gms_sha256=2b30f9fcc061b57456cbe38ddc0f13c88863bad49557508a9196f2d1c4cb17a5
	;;
*)
	echo "unsupported architecture: ${TARGETARCH}" >&2
	exit 1
	;;
esac
fetch() {
	curl -fsSL --retry 3 --retry-delay 2 --max-time 600 "$1" -o "$2"
	actual="$(sha256sum "$2" | cut -d' ' -f1)"
	if [ "${actual}" != "$3" ]; then
		echo "checksum mismatch for $1: got ${actual}, want $3" >&2
		exit 1
	fi
}
mkdir -p /tmp/dl /out/usr/local/bin
cd /tmp/dl
# mq 0.8.2, the jq-like query tool for Markdown.
fetch "https://github.com/harehare/mq/releases/download/v0.8.2/mq-${mq_target}" mq "${mq_sha256}"
install -m 0755 mq /out/usr/local/bin/mq
# okfctl 0.4.0, the OKF bundle tool. Only okfctl is extracted: the archive also
# carries okfctl-search, whose semantic index needs a model download from a
# host that is not allowlisted.
fetch "https://github.com/cwest/okfctl/releases/download/v0.4.0/okfctl_0.4.0_linux_${TARGETARCH}.tar.gz" \
	okfctl.tar.gz "${okfctl_sha256}"
tar xzf okfctl.tar.gz okfctl
install -m 0755 okfctl /out/usr/local/bin/okfctl
# github-mcp-server 1.12.2, which Pi runs over stdio (files/home/.pi/agent/
# mcp.json). The same SHA-256 values sbxagent pins for these archives.
fetch "https://github.com/github/github-mcp-server/releases/download/v1.12.2/github-mcp-server_${gms_asset}.tar.gz" \
	gms.tar.gz "${gms_sha256}"
tar xzf gms.tar.gz github-mcp-server
install -m 0755 github-mcp-server /out/usr/local/bin/github-mcp-server
# Release tarballs keep the packer's uid, so the whole tree goes to root.
chown -R 0:0 /out
FETCH

# Pi's config, owned by the agent. /home and /home/agent keep the owners the
# base gives them. COPY does not reliably carry the git 100755 bit, so the
# gate script's mode is set explicitly.
FROM debian:trixie-slim AS assemble
COPY files/home/ /src/home/
RUN <<'ASSEMBLE'
set -eu
install -d -o 0 -g 0 -m 0755 /out/home
install -d -o 1000 -g 1000 -m 0755 /out/home/agent
cp -R /src/home/. /out/home/agent/
find /out/home/agent -type d -exec chmod 0755 {} +
find /out/home/agent -type f -exec chmod 0644 {} +
chmod 0755 /out/home/agent/.pi/agent/skills/compile-okf/scripts/check-okf.sh
chown -R 1000:1000 /out/home/agent
ASSEMBLE

# Docker's own Pi image (docker/sbx-kits-contrib, pi/Dockerfile), reused as a
# base. It is the shell-docker template plus Pi, installed with
# `npm install -g` as the agent user, `fd-find` with an `fd` link, and the
# `pi` flavor label that `sbx ls` reports. Its NPM_CONFIG_PREFIX
# (/usr/local/share/npm-global) is owned by the agent user, so the user-1000
# `npm install --global` hooks keep working.
#
# The tag is rebuilt nightly against Pi's npm `latest`, so it is pinned by its
# index digest instead. That freezes Pi, the npm dependency tree it resolved
# without a lockfile (Pi stopped shipping one in 1.0.1), and the shell-docker
# template beneath it, for both architectures at once. Template fixes
# therefore reach this kit only with a new digest; the README's "Bumping Pi"
# has the check to run before bumping.
FROM docker.io/sbx/pi-image@sha256:134b48cfc7b83a270d12d2c0ad0b7b7d0d40ffedf7dd567792246a9215a1d2d5
COPY --from=fetch /out/ /
COPY --from=assemble /out/ /
# MIGRATION NOTE: see the descriptor. Turns off the base's v2 transition
# label, which some runtimes still honour by starting Docker.
LABEL com.docker.sandboxes.start-docker="false"
USER agent
# Model and provider come from the kit's own config (settings.json +
# models.json in ~/.pi/agent/), so no --provider/--model flags here. This
# replaces the base's tini entrypoint, as the v2 kit's did, and clears its
# inherited CMD (`pi`), which would otherwise be a stray argument.
ENTRYPOINT ["pi"]
