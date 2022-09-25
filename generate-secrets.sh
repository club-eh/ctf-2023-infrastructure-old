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


# colored output
if which tput >/dev/null 2>&1; then
	C_GREEN="$(tput setaf 2)"
	C_LBLUE="$(tput setaf 12)"
	C_RESET="$(tput sgr0)"
else
	C_GREEN=""
	C_LBLUE=""
	C_RESET=""
fi
msg_action() { echo "$C_GREEN""$@""$C_RESET"; }
msg_info() { echo "$C_LBLUE""$@""$C_RESET"; }


SCRIPT_DIR="$(dirname "$(realpath "$0")")"  # determine location of this script
TARGET_DIR="${SCRIPT_DIR}/secrets/${ENVIRONMENT}"

# create secrets directory for this environment
mkdir -p "$TARGET_DIR"


# generate SSH keypair for management account
if [[ ! -f "$TARGET_DIR"/management_ssh_key ]]; then
	msg_action "> generating management SSH key"
	ssh-keygen -q -N "" -t ed25519 -f "$TARGET_DIR"/management_ssh_key -C "Management SSH key (${ENVIRONMENT} env)"
else
	msg_info "> management SSH key already exists, skipping"
fi


# generate per-host root keys
mkdir -p "$TARGET_DIR"/hostkeys
for machine in "ctf-flagship" "ctf-challenges-1"; do
	machine_rootkey="${TARGET_DIR}/hostkeys/${machine}.key"
	if [[ ! -f "$machine_rootkey" ]]; then
		msg_action "> generating host root key for ${machine}"
		touch "$machine_rootkey"
		chmod 600 "$machine_rootkey"
		head -c 256 /dev/urandom > "$machine_rootkey"
	else
		msg_info "> host root key for ${machine} already exists, skipping"
	fi
done


# obtain SSL certificates
if [[ ! -f "${TARGET_DIR}/ssl-certificate.pem" ]]; then
	case "$ENVIRONMENT" in
		local)
			msg_action "> generating self-signed SSL certificate"
			# generate self-signed certificates
			OPENSSL_ARGS=(
				-new
				-x509
				-nodes
				-days 365
				-newkey ec
				-pkeyopt ec_paramgen_curve:prime256v1
				-subj "/CN=ctf-flagship"
				-keyout "${TARGET_DIR}/ssl-certificate.key"
				-out "${TARGET_DIR}/ssl-certificate.pem"
			)
			openssl req "${OPENSSL_ARGS[@]}"
		;;
		production|staging)
			# obtain Let's Encrypt certificates (TODO)
			echo "> WARNING: SSL certificate generation not implemented!"
		;;
	esac
else
	msg_info "> SSL certificate already exists, skipping"
fi
