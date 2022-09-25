from util import get_secrets_dir


# Declare environment name
env_name = "local"

# Use environment-specific SSH key
ssh_key = get_secrets_dir(env_name) / "management_ssh_key"

# Disable known hosts file for local test environment
ssh_known_hosts_file = "/dev/null"
ssh_strict_host_key_checking = "no"

# We're using self-signed certificates
self_signed_certs = True
