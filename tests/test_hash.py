import hashlib

import pytest

from zah.hash import algorithms, hash_file


def test_algorithms_is_based_on_hashlib_algorithms_guaranteed():
    """
    Test if the `algorithms` list matches the `hashlib.algorithms_guaranteed` set, which contains
    algorithms guaranteed to be supported on all platforms. The function ensures the `algorithms`
    collection is correctly implemented as a list of unique algorithm names and validates each
    element as a string.

    :raises AssertionError: If `algorithms` is not a list, if its contents do not match
        `hashlib.algorithms_guaranteed` by set comparison, or if any element in `algorithms`
        is not a string.
    :rtype: None
    """
    assert isinstance(algorithms, list)
    # Order is not important, compare as sets
    assert set(algorithms) == set(hashlib.algorithms_guaranteed)
    # All entries must be strings
    assert all(isinstance(a, str) for a in algorithms)


def test_hash_file_default_algorithm_matches_hashlib(tmp_path):
    """
    Tests if the default algorithm used by the `hash_file` function matches the output
    of the `hashlib.sha256` implementation. This ensures that the hashing function
    provides consistent and correct results using the expected algorithm.

    :param tmp_path: Provides a temporary directory unique to the test invocation.
    :type tmp_path: pathlib.Path
    :return: None. The test passes if the assertion succeeds and fails otherwise.
    """
    file_path = tmp_path / "data.bin"
    data = b"some test data for hashing"
    file_path.write_bytes(data)

    expected = hashlib.sha256(data).hexdigest()
    result = hash_file(file_path)

    assert result == expected


def test_hash_file_with_explicit_algorithm_md5(tmp_path):
    """
    Tests the `hash_file` function when using an explicit hash algorithm `md5`.

    Evaluates if the function correctly computes the hash of a file's content
    when the `algorithm` parameter is explicitly specified as `md5`.

    :param tmp_path: A temporary path object provided by pytest for creating
        and managing temporary files or directories.
    :return: None
    """
    file_path = tmp_path / "data_md5.bin"
    data = b"another payload with different content"
    file_path.write_bytes(data)

    expected = hashlib.md5(data).hexdigest()
    result = hash_file(file_path, algorithm="md5")

    assert result == expected


def test_hash_file_reads_in_multiple_chunks(tmp_path):
    """
    Test the `hash_file` function to verify that it reads files in multiple
    chunks correctly and computes the hash accurately, even for large files
    that require multiple iterations of reading.

    :param tmp_path: Temporary path fixture provided by pytest for creating
        and managing files during the test.
    :return: None
    """
    file_path = tmp_path / "large.bin"
    chunk_size = 1024 * 1024
    size = chunk_size * 2 + 123  # Ensure at least three iterations
    data = b"a" * size
    file_path.write_bytes(data)

    expected = hashlib.sha256(data).hexdigest()
    result = hash_file(file_path, algorithm="sha256")

    assert result == expected


def test_hash_file_raises_for_unknown_algorithm(tmp_path):
    """
    Tests that the `hash_file` function raises a `ValueError` when an unknown
    hashing algorithm is provided.

    This function creates a temporary file with sample content and invokes
    `hash_file` with an invalid hashing algorithm name. It asserts that the
    correct exception is raised.

    :param tmp_path: Path object provided by pytest to create temporary files
                     and directories.
    :type tmp_path: pathlib.Path
    """
    file_path = tmp_path / "data_unknown.bin"
    file_path.write_text("content")

    with pytest.raises(ValueError):
        hash_file(file_path, algorithm="non_existing_algorithm")


def test_hash_file_raises_for_missing_file(tmp_path):
    """
    Tests that the `hash_file` function raises a `FileNotFoundError` when attempting
    to hash a file that does not exist.

    :param tmp_path: Temporary test directory provided by pytest.
    :type tmp_path: pathlib.Path
    """
    missing_path = tmp_path / "missing.bin"

    with pytest.raises(FileNotFoundError):
        hash_file(missing_path)
