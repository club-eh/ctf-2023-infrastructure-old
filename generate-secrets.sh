#!/bin/bash

set -euo pipefail


if ((BASH_VERSINFO[0] < 4)); then
	echo "Sorry, this script requires bash 4.0+" >&2
	exit 1
fi


## arg parsing

show_help() {
	echo "usage: $0 <production|staging|local> [options]"
	echo
	echo "  --renew       - renew existing SSL certificates"
	echo "  --no-staging  - use the production Let's Encrypt ACME servers"
	exit 1
}

while (($#>0)); do
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
		--new)
			LE_RENEW_CERTS=1
			;;
		--no-staging)
			LE_USE_PROD=1
			;;
		*)
			show_help
			;;
	esac
	shift
done

if [[ -z "${ENVIRONMENT:-}" ]]; then
	show_help
fi


# define constants for colored output
if which tput >/dev/null 2>&1; then
	C_GREEN="$(tput setaf 2)"
	C_LBLUE="$(tput setaf 12)"
	C_RED="$(tput setaf 1)"
	C_YELLOW="$(tput setaf 3)"
	C_RESET="$(tput sgr0)"
else
	C_GREEN=""
	C_LBLUE=""
	C_RED=""
	C_YELLOW=""
	C_RESET=""
fi

# helper functions
msg_action() { echo "$C_GREEN""$@""$C_RESET"; }
msg_info() { echo "$C_LBLUE""$@""$C_RESET"; }
msg_warn() { echo "$C_YELLOW""$@""$C_RESET"; }
msg_error() { echo "$C_RED""$@""$C_RESET"; }
confirm_action() {
	read -rp "$1" ANS
	case "$ANS" in
		y|Y)
			return 0
			;;
		*)
			return 1
			;;
	esac
}


SCRIPT_DIR="$(dirname "$(realpath "$0")")"  # determine location of this script
TARGET_DIR="${SCRIPT_DIR}/secrets/${ENVIRONMENT}"

# create secrets directory for this environment
mkdir -p "$TARGET_DIR"


### define generation functions

generate_management_ssh_key() {
	if [[ ! -f "$TARGET_DIR"/management_ssh_key ]]; then
		msg_action "> generating management SSH key"
		ssh-keygen -q -N "" -t ed25519 -f "$TARGET_DIR"/management_ssh_key -C "Management SSH key (${ENVIRONMENT} env)"
	else
		msg_info "> management SSH key already exists, skipping"
	fi
}

generate_host_root_keys() {
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
}

generate_ssl_certs() {
	if [[ ! -f "${TARGET_DIR}/ssl-certificate.pem" || -n "${LE_RENEW_CERTS:-}" ]]; then
		case "$ENVIRONMENT" in
			local)
				msg_action "> generating self-signed SSL certificate for local environment"
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
				# obtain Let's Encrypt certificates

				# select base domain name
				if [[ "$ENVIRONMENT" == "production" ]]; then
					base_domain="ctf-2023.clubeh.ca"
				else
					base_domain="ctf-2023-staging.clubeh.ca"
				fi

				# sanity checks
				if ! which lego >/dev/null 2>&1; then
					msg_error "\`lego\` program not found, skipping SSL certificates"
					return
				elif [[ -z "${CF_DNS_API_TOKEN:-}" ]]; then
					msg_error "CF_DNS_API_TOKEN environment variable not set, skipping SSL certificates"
					return
				fi

				LEGO_ARGS=(
					--accept-tos
					--path "${SCRIPT_DIR}/secrets/.lego"
					--email "ethicalhackingclub@outlook.com"
					--dns cloudflare
					--domains "${base_domain}"
					--domains "*.${base_domain}"
				)

				# select ACME server
				if [[ -n "${LE_USE_PROD:-}" ]]; then
					LEGO_ARGS+=(--server 'https://acme-v02.api.letsencrypt.org/directory')
				else
					LEGO_ARGS+=(--server 'https://acme-staging-v02.api.letsencrypt.org/directory')
				fi

				# select action
				if [[ -n "${LE_RENEW_CERTS:-}" ]]; then
					LEGO_ARGS+=("renew")
					msg_action "> renewing Let's Encrypt certificate for ${ENVIRONMENT} environment (${base_domain})"
				else
					LEGO_ARGS+=("run")
					msg_action "> obtaining Let's Encrypt certificate for ${ENVIRONMENT} environment (${base_domain})"
				fi

				msg_warn "> this is a potentially destructive action. make sure you understand what you are doing!"
				if confirm_action "${C_YELLOW}> are you sure you want to proceed? (y/N) ${C_RESET}"; then
					# execute action
					lego "${LEGO_ARGS[@]}"

					# create symlinks
					ln -sf "../.lego/certificates/${base_domain}.key" "${TARGET_DIR}/ssl-certificate.key"
					ln -sf "../.lego/certificates/${base_domain}.crt" "${TARGET_DIR}/ssl-certificate.pem"
				else
					msg_info "> certificate action cancelled"
				fi
			;;
		esac
	else
		msg_info "> SSL certificate already exists, skipping"
	fi
}


# run generation functions
generate_management_ssh_key
generate_host_root_keys
generate_ssl_certs
