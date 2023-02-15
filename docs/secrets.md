# Secrets


## API Tokens

### Cloudflare

This token grants limited access to the `clubeh.ca` domain.

Used by:
- Terraform (to edit DNS records)
- Lego (to generate Let's Encrypt certificates)

To generate a new token:

1. Login to https://dash.cloudflare.com/
2. Go to https://dash.cloudflare.com/profile/api-tokens
3. Create a new API token
4. Under "Permissions", add:
	- `Zone:DNS:Edit` - required by Terraform to edit DNS records
	- `Zone:Zone:Read` - required by Lego to automatically determine the Zone ID
5. Under "Zone Resources", add:
	- Include > Specific zone > `clubeh.ca`
6. Optionally, set a TTL
7. Create the token and store it as `/secrets/api_token_cloudflare`


### Proxmox

# TODO
