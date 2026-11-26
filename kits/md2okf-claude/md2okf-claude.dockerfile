# Content recipe for md2okf-claude.yaml beside it. The result is a mixin: one
# overlay layer that lands on the claude workload's filesystem, so it carries
# only what this kit adds. Package installs are not here: they run as install
# hooks against the workload's own package database (see the descriptor).
#
# The overlay stays out of /home entirely. Whatever the workload keeps there
# is its own, and the trace directory md2okf mounts at ~/.claude/projects
# needs nothing from this layer.

# The two pinned release binaries, downloaded and checksummed in a throwaway
# stage, so neither Debian nor curl ends up in the mixin. Pinning the digests
# here, rather than reading each release's checksums file, means a re-uploaded
# asset fails the build too. Identical in kits/md2okf-codex and kits/md2okf-pi.
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
	;;
arm64)
	mq_target=aarch64-unknown-linux-gnu
	mq_sha256=adc63fb3f1f01d3fe35f56deb5e09ab19f7f57142fcd7e2c8c0004fff6ed84c3
	okfctl_sha256=09821344881af75dde68476d3177363f915380ae43fea815b62b785109f7ec0a
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
# Release tarballs keep the packer's uid; on an unknown base that uid may be a
# real account, so the whole tree goes to root.
chown -R 0:0 /out
FETCH

# The skills, root-owned and read-only to the agent, under a kit-specific
# prefix. The descriptor's agent-skill@1 entries name each directory, and the
# runtime exposes them in ~/.claude/skills. COPY does not reliably carry the
# git 100755 bit, so the gate script's mode is set explicitly.
FROM debian:trixie-slim AS assemble
COPY files/skills/ /src/skills/
RUN <<'ASSEMBLE'
set -eu
install -d -o 0 -g 0 -m 0755 /out/usr/share/md2okf-claude
cp -R /src/skills /out/usr/share/md2okf-claude/skills
find /out -type d -exec chmod 0755 {} +
find /out -type f -exec chmod 0644 {} +
chmod 0755 /out/usr/share/md2okf-claude/skills/compile-okf/scripts/check-okf.sh
chown -R 0:0 /out
ASSEMBLE

FROM scratch
COPY --from=fetch /out/ /
COPY --from=assemble /out/ /
