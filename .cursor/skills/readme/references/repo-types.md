# Repository types

Classify first, then read only the section that applies. The standard library
shape is the wrong shape for most of these.

## Library, SDK or package

The canonical case. Import plus minimal usage in the first screen, then the
API surface, the stability and versioning policy, and the supported runtime
range. The install command must be the published one and the package name must
match the registry. Mention the dependency footprint or bundle size if it is a
real consideration for adopters.

## CLI tool

Show invocations and their output, not source snippets. Include a `--help`
excerpt. Cover every installation channel — package manager, install script,
prebuilt binary, container — and state the platform matrix explicitly. A
terminal recording helps more here than anywhere else, but never replaces
text the reader can copy and paste.

## Application or self-hosted service

The reader is asking "can I run this, and what will it cost me". Needs a
screenshot — the one type where the visual is load-bearing, though whatever it
shows must still be stated in text — deployment options (a Compose file, a chart, a managed alternative), system
requirements, configuration and secrets handling, the backup and upgrade path,
and a security note. A working deployment file matters more than usage
examples.

## Framework or meta-tool

The one type where a long essay README is the right answer. Needs a philosophy
or design-principles section, an ecosystem map, and an honest comparison with
the incumbent framework it expects to displace.

## Research, data or paper code

Different contract: reproducibility, not adoption. Needs the paper citation
and BibTeX, dataset provenance and licensing (often distinct from the code
license), exact environment pinning, hardware requirements and expected
runtime, a results table carrying the numbers the paper claims, and an honest
statement of what is and is not reproducible. Structure it as motivation →
method and results → repository overview.

## Internal company repository

No adoption funnel. The reader is a new team member or an on-call engineer.
Needs ownership (team, chat channel, on-call rota), local setup that works on
a fresh machine, how to run the tests, deployment and rollback, environment
topology, and links to dashboards, runbooks and design docs. Drop badges,
contributing, license and acknowledgements entirely.

## Monorepo root

The root README is a directory, not a project page: what the repo contains, a
table of packages each linking to its own README, the shared tooling, and how
to build and test everything. Depth belongs in the per-package READMEs, not
here.

## Curated list or documentation repository

Install and usage do not apply and should be omitted, not stubbed. The
contribution criteria — what qualifies for inclusion — matter more than
anything else on the page.

## Template, starter or boilerplate

Must clearly separate "how to use this template" from "the README the
generated project will end up with". Shipping the template's own README as the
generated project's README is a common and embarrassing failure.

## Plugin or extension

State the host application and the compatible version range in the first
screen. That range is the primary disqualifier, so it goes above everything
except the name and the one-liner.
