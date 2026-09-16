#!/bin/sh
# Relocate an agent's trace folder onto this sandbox's state mount.
# Usage: sh mount-state.sh LINK SUBDIR
#
# A bind mount keeps LINK as a real directory while making its writes land in
# host-backed state. It must be recreated after every sandbox start.
set -eu
[ -n "${SBXAGENT_STATE_DIR:-}" ] || exit 0
link="$1"
target="${SBXAGENT_STATE_DIR}/$2"

same_fs() {
	one="$(stat -c '%d:%i' "$1" 2>/dev/null || stat -f '%d:%i' "$1" 2>/dev/null)"
	two="$(stat -c '%d:%i' "$2" 2>/dev/null || stat -f '%d:%i' "$2" 2>/dev/null)"
	[ -n "${one}" ] && [ "${one}" = "${two}" ]
}

mkdir -p "${target}" || {
	echo "mount-state: could not create ${target}" >&2
	exit 1
}
mkdir -p "${link}" || {
	echo "mount-state: could not create ${link}" >&2
	exit 1
}

# shellcheck disable=SC2310 # false normally means "not bound yet"
if same_fs "${link}" "${target}"; then
	exit 0
fi

# Host state is authoritative. Merge only names absent from it, including
# dotfiles, before covering the stock directory with the bind mount.
for entry in "${link}"/.[!.]* "${link}"/..?* "${link}"/*; do
	[ -e "${entry}" ] || continue
	name="$(basename "${entry}")"
	[ "${name}" = "lost+found" ] && continue
	[ -e "${target}/${name}" ] && continue
	if ! cp -R "${entry}" "${target}/"; then
		echo "mount-state: could not copy ${link}/${name} into ${target}" >&2
		exit 1
	fi
done

if ! sudo -n mount --bind "${target}" "${link}"; then
	echo "mount-state: could not bind-mount ${target} onto ${link}" >&2
	exit 1
fi
