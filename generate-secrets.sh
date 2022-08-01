#!/bin/bash

set -euo pipefail


if ((BASH_VERSINFO[0] < 4)); then
	echo "Sorry, this script requires bash 4.0+" >&2
	exit 1
fi


show_help() {
	echo "usage: $0 <production|staging|local>"
	exit 1
}

if (($# != 1)); then
	show_help
fi

case "$1" in
	production)
		ENVIRONMENT="production"
		;;
	staging)
		ENVIRONMENT="staging"
		;;
	local)
		ENVIRONMENT="local"
		;;
	*)
		show_help
		;;
esac


SCRIPT_DIR="$(dirname "$(realpath "$0")")"  # determine location of this script
TARGET_DIR="${SCRIPT_DIR}/secrets/${ENVIRONMENT}"

# create secrets directory for this environment
mkdir -p "$TARGET_DIR"


# generate SSH keypair for management account
if [[ ! -f "$TARGET_DIR"/management_ssh_key ]]; then
	echo "> generating management SSH key"
	ssh-keygen -q -N "" -t ed25519 -f "$TARGET_DIR"/management_ssh_key -C "Management SSH key (${ENVIRONMENT} env)"
else
	echo "> management SSH key already exists, skipping"
fi
