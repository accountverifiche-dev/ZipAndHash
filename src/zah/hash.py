import hashlib
from typing import List
from pathlib import Path


__all__ = ["algorithms", "hash_file"]


algorithms: List[str] = list(hashlib.algorithms_guaranteed)


def hash_file(file_path: Path, algorithm: str = "sha256") -> str:
    """
    Compute the hash of a file using the specified hashing algorithm. This function reads
    the file in chunks to avoid excessive memory usage for large files. A default hashing
    algorithm can be specified, which is "sha256" if not provided.

    :param file_path: The path to the file to be hashed.
    :type file_path: Path
    :param algorithm: The hashing algorithm to use, e.g., 'sha256', 'md5'. Defaults to "sha256".
    :type algorithm: str
    :return: The hexadecimal digest of the file's contents using the specified algorithm.
    :rtype: str
    """
    hasher = hashlib.new(algorithm)

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):  # 1MB per chunk
            hasher.update(chunk)

    return hasher.hexdigest()
