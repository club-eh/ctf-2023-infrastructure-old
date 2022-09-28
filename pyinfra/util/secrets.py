from pathlib import Path

from pyinfra import host
from pyinfra.api import DeployError


BASE_DIRECTORY = Path("../secrets")


def get_secrets_dir(env_name: str | None = None) -> Path:
	"""Returns the path to the secrets directory for this deploy environment.

	Args:
		env_name (optional): The environment for which to return a secrets directory.
		Defaults to the current host's env_name.
	"""

	# default to current host's environment
	if env_name is None:
		env_name = host.data.env_name

		if env_name is None:
			raise DeployError("Could not determine environment from current host (missing `env_name` data)")

	secrets_dir =  BASE_DIRECTORY / env_name

	# ensure the path exists
	if not secrets_dir.exists():
		raise DeployError(f"Secrets directory not found (should be at '{secrets_dir}')")

	return secrets_dir
