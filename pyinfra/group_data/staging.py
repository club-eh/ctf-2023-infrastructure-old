from util import get_secrets_dir


# Declare environment name
env_name = "staging"

# Use environment-specific SSH key
ssh_key = get_secrets_dir(env_name) / "management_ssh_key"

# We're using self-signed certificates (TODO: remove)
self_signed_certs = True
