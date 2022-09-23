from pathlib import Path

from pyinfra import host


BASE_DIRECTORY = Path("../secrets")


def get_secrets_dir(env_name: str | None = None) -> Path:
	"""Returns the path to the secrets directory for this deploy environment.

	Args:
		env_name (optional): The environment to . Defaults to the current host's env_name.
	"""

	if env_name is None:
		env_name = host.data.env_name

	return BASE_DIRECTORY / env_name
