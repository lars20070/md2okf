FROM node:24.16.0-bookworm-slim

# Pin the Pi coding agent version. This runtime pins independently of the
# sandbox (pi/sandbox/spec.yaml pins its own); there is deliberately no
# cross-runtime version check, so either runtime can be deleted cleanly.
ARG PI_VERSION=0.82.1

# Pin OKF linter `okf-lint` independently too. 
# https://github.com/thisismydesign/okf-lint
ARG OKF_LINT_VERSION=0.1.0

RUN apt-get update \
  && apt-get install -y --no-install-recommends bash ca-certificates git ripgrep fd-find \
  && ln -s /usr/bin/fdfind /usr/local/bin/fd \
  && rm -rf /var/lib/apt/lists/*
RUN npm install -g --ignore-scripts \
  "@earendil-works/pi-coding-agent@${PI_VERSION}" \
  "@thisismydesign/okf-lint@${OKF_LINT_VERSION}"

# Pre-create the agent state dir owned by the non-root runtime user so the
# root-initialized named volume mounted there stays writable under --user 1000
# and --read-only.
RUN mkdir -p /home/node/.pi/agent && chown -R node:node /home/node

WORKDIR /workspace
COPY SPEC.md /workspace/SPEC.md
RUN chown node:node /workspace/SPEC.md
USER node
ENTRYPOINT ["pi"]