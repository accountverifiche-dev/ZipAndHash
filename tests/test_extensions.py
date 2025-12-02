from typing import Iterable

from zah.extensions import allowed_ext


def test_allowed_ext_is_set_of_strings():
    """
    Tests if the variable `allowed_ext` is a set of strings.

    It ensures that `allowed_ext` is correctly defined as a set data structure
    and that all its members are of type string.

    :return: None
    :rtype: None
    """
    assert isinstance(allowed_ext, set)
    assert all(isinstance(ext, str) for ext in allowed_ext)


def test_allowed_ext_entries_have_leading_dot_and_no_spaces():
    """
    Checks if entries in the `allowed_ext` list follow expected formatting rules.

    This function ensures that each entry in the `allowed_ext` list starts with a dot (.)
    and does not contain any spaces. It iterates through the entries and validates these
    conditions using assertions.

    :return: None
    """
    for ext in allowed_ext:
        assert ext.startswith(".")
        assert " " not in ext


def test_allowed_ext_contains_common_expected_extensions():
    """Check presence of a few representative extensions from different groups."""
    expected = {
        ".txt",    # text
        ".pdf",    # documents
        ".png",    # images
        ".mp4",    # video
        ".mp3",    # audio
        ".zip",    # archive
        ".py",     # code
        ".sql",    # data/db
    }
    for ext in expected:
        assert ext in allowed_ext


def test_allowed_ext_has_no_duplicates():
    """
    Tests whether the list `allowed_ext` contains duplicate elements. This test verifies
    that all elements in the list are unique by comparing the total count of elements
    with the count of unique elements.

    :raises AssertionError: If the total count of elements differs from the count of
        unique elements.
    """
    def count(iterable: Iterable[str]) -> int:
        c = 0
        for _ in iterable:
            c += 1
        return c

    total = count(allowed_ext)
    unique = count(set(allowed_ext))
    assert total == unique
