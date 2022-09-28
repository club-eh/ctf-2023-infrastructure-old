"""Utilities for computing file paths."""

import inspect
from pathlib import Path

from pyinfra import host
from pyinfra.api import DeployError


# Absolute path of the base roles/ subdirectory
_ROLES_DIRECTORY_PATH = (Path(__file__).parents[1] / "roles").resolve()
# Absolute path of the base secrets/ subdirectory
_SECRETS_DIRECTORY_PATH = (Path(__file__).parents[2] / "secrets").resolve()


def get_role_path() -> Path:
	"""Returns the current role's base directory path.
	
	Example:
	```py
	# roles/my_role/sub_module.py:
	>>> get_role_path()
	Path("roles/my_role")
	```
	"""

	# retrieve current stack frame
	frame = inspect.currentframe()
	if frame is None:
		raise Exception("Python interpreter does not support inspect.currentframe()")

	# switch to caller's frame
	frame = frame.f_back

	# walk up the call stack until we find a submodule of roles
	while frame is not None:
		module_path_str: str | None = frame.f_globals.get("__file__")
		if module_path_str is not None:
			module_path = Path(module_path_str)
			try:
				local_path = module_path.relative_to(_ROLES_DIRECTORY_PATH)
			except ValueError:
				pass
			else:
				# found a module under roles/
				role_name = local_path.parts[0]
				return _ROLES_DIRECTORY_PATH / role_name

		# couldn't find a match, move up the call stack and try again
		frame = frame.f_back

	# reached end of call stack without finding a suitable 
	raise Exception("Unable to determine role directory: current frame is None")

def get_file_path(filename: str) -> Path:
	"""Returns the filepath for a given local file resource (under the current role).

	Convenience wrapper around `get_role_path()`.
	"""

	return get_role_path() / "files" / filename


def get_secrets_dir(env_name: str | None = None) -> Path:
	"""Returns the path to the secrets directory for this deploy environment.

	Args:
		env_name (optional): The environment to return a directory path for.
		Defaults to the current host's env_name.
	"""

	# default to current host's environment
	if env_name is None:
		env_name = host.data.env_name

		if env_name is None:
			raise DeployError("Could not determine environment from current host (missing `env_name` data)")

	secrets_dir = _SECRETS_DIRECTORY_PATH / env_name

	# ensure the path exists
	if not secrets_dir.exists():
		raise DeployError(f"Secrets directory not found (should be at '{secrets_dir}')")

	return secrets_dir

def get_secret_path(filename: str, env_name: str | None = None) -> Path:
	"""Returns the filepath for a given secret file.

	Convenience wrapper around `get_secrets_dir()`.

	Args:
		filename (str): Relative path to the file.
		env_name (optional): The environment to return a filepath for.
		Defaults to the current host's env_name.
	"""

	filepath = get_secrets_dir(env_name=env_name) / filename

	if not filepath.exists():
		raise DeployError(f"Secret '{filename}' not found for '{env_name}' environment")

	return filepath
