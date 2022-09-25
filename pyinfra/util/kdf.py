# Key Derivation Function

from typing import Generic, TypeVar

import base64
import hmac
import math
import uuid
from pathlib import Path

import blake3

from pyinfra.api import Host

from util import get_secrets_dir


HOST_KEY_SIZE = 256


S = TypeVar("S")

class WrappedSecret(Generic[S]):
	"""Wraps a secret value to avoid accidentally leaking it.

	Note that this class DOES NOT encrypt or otherwise protect the value from a local attacker.
	It is designed only to avoid accidentally revealing the value to, for example, a log file.
	"""

	__slots__ = ("_secret",)

	def __init__(self, secret: S):
		self._secret = secret

	def unwrap(self) -> S:
		"""Return the stored value of the secret."""
		return self._secret

	def __repr__(self) -> str:
		return "WrappedSecret(<hidden>)"

	def __str__(self) -> str:
		return self.__repr__()

HostKeyValue = WrappedSecret[bytes]


class MissingHostKey(Exception):
	"""Raised by KeySource methods when a valid host key could not be found."""

class KeySource:
	"""Derives deterministic host-specific keys, for use as database passwords, encryption keys, etc."""

	_hash_func = blake3.blake3
	_hash_func_sz: int = _hash_func.digest_size

	@classmethod
	def _hmac_func(cls, key: bytes, msg: bytes) -> bytes:
		return hmac.new(key, msg, cls._hash_func).digest()

	@classmethod
	def _hkdf_b3(cls, root_km: bytes, label: bytes, length: int = 32) -> bytearray:
		"""Loose adaptation of RFC5869 HKDF using blake3."""

		if length / cls._hash_func_sz >= 255:
			raise ValueError(f"Requested key length {length} is too high!")

		# use RFC5869-compliant salt
		salt = bytes(length)

		prk = cls._hmac_func(salt, root_km)

		t = bytes()
		output = bytearray()

		for i in range(math.ceil(length / cls._hash_func_sz)):
			t = cls._hmac_func(prk, t + label + bytes([i + 1]))
			output.extend(t)

		return output[:length]

	@classmethod
	def derive_key(cls, host: Host, identifier: str, length: int) -> bytearray:
		"""Derive a unique key from a host-specific root key and a key-specific identifier.

		Args:
			identifier (str): A unique identifier for this specific key. Example: "wireguard-internal-network-1"
			length (int): The length of the derived key, in bytes.

		Raises:
			MissingHostKey: If the current host does not have a valid host key.

		Returns:
			The derived key as raw bytes.
		"""

		# retrieve host root key from memory, if previously loaded
		loaded_host_key = host.data.get("__loaded_host_root_key", None)
		if loaded_host_key is None:
			# validate file
			host_key_path: Path = get_secrets_dir(host.data.env_name) / "hostkeys" / f"{host.data.hostname}.key"
			if not host_key_path.exists():
				raise MissingHostKey(f"Host key file not found ({host_key_path})")
			elif host_key_path.stat().st_size != HOST_KEY_SIZE:
				raise MissingHostKey(f"Host key file does not have expected size ({host_key_path.stat().st_size} != {HOST_KEY_SIZE})")
			# read file into memory
			with host_key_path.open(mode="rb") as fp:
				loaded_host_key = WrappedSecret(fp.read())
			# cache for later use
			host.data.__loaded_host_root_key = loaded_host_key

		# TODO: potentially retrieve another key from user somehow?
		shared_key = b""

		# derive and return new key
		return cls._hkdf_b3(loaded_host_key.unwrap() + shared_key, identifier.encode(), length)

	@classmethod
	def derive_key_b64(cls, host: Host, identifier: str, length: int) -> str:
		"""Derive a unique key from a host-specific root key and a key-specific identifier.

		Args:
			identifier (str): A unique identifier for this specific key. Example: "wireguard-internal-network-1"
			length (int): The length of the derived key, in bytes.

		Raises:
			MissingHostKey: If the current host does not have a valid host key.

		Returns:
			The derived key as a base64-encoded string.
		"""

		raw_key = cls.derive_key(host, identifier, length)

		return base64.b64encode(raw_key).decode()

	@classmethod
	def derive_key_uuid(cls, host: Host, identifier: str) -> str:
		"""Derive a unique key from a host-specific root key and a key-specific identifier.

		Formats the derived key as a UUIDv4.

		Args:
			identifier (str): A unique identifier for this specific key. Example: "wireguard-internal-network-1"

		Raises:
			MissingHostKey: If the current host does not have a valid host key.

		Returns:
			The derived key as a UUIDv4 string.
		"""

		raw_key = cls.derive_key(host, identifier, 16)

		return str(uuid.UUID(version=4, bytes=raw_key))
