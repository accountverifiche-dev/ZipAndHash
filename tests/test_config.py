from pathlib import Path
from dataclasses import FrozenInstanceError

import pytest

from zah.config import Config


def test_config_creation_with_copy_path():
    """
    Tests the creation of a `Config` object with a specified copy path and ensures
    that all attributes are correctly assigned and functional. Validates the
    behavior of the `Config` initialization using provided paths and optional
    parameters.

    :return: None
    """
    src = Path("/tmp/src")
    dst = Path("/tmp/dst")
    cpy = Path("/tmp/cpy")

    cfg = Config(
        src=src,
        dst=dst,
        sub_dir=True,
        hash="sha3_256",
        mv=True,
        cpy=cpy,
        fil_zip=True,
        fil_cpy=True,
        fil_mv=True,
        fil_empty=True,
        safe=False,
        debug=True,
    )

    assert cfg.src == src
    assert cfg.dst == dst
    assert cfg.sub_dir is True
    assert cfg.hash == "sha3_256"
    assert cfg.mv is True
    assert cfg.cpy == cpy
    assert cfg.fil_zip is True
    assert cfg.fil_cpy is True
    assert cfg.fil_mv is True
    assert cfg.fil_empty is True
    assert cfg.safe is False
    assert cfg.debug is True


def test_config_creation_without_copy_path():
    """
    Tests the creation of a `Config` instance without a specified copy path.

    This test checks the proper instantiation of the `Config` class when specific
    parameters are provided, ensuring that attributes are correctly assigned and
    default values are handled as expected. It validates both the provided values
    for attributes like `src`, `dst`, `sub_dir`, `hash`, and others, as well as
    defaults where applicable.

    :return: None
    """
    src = Path("src")
    dst = Path("dst")

    cfg = Config(
        src=src,
        dst=dst,
        sub_dir=False,
        hash="md5",
        mv=False,
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=False,
        fil_empty=False,
        safe=True,
        debug=False,
    )

    assert cfg.src == src
    assert cfg.dst == dst
    assert cfg.sub_dir is False
    assert cfg.hash == "md5"
    assert cfg.mv is False
    assert cfg.cpy is None
    assert cfg.fil_zip is False
    assert cfg.fil_cpy is False
    assert cfg.fil_mv is False
    assert cfg.fil_empty is False
    assert cfg.safe is True
    assert cfg.debug is False


def test_config_is_frozen_immutable():
    """
    Test function to verify that the `Config` instance is immutable and raises a
    `FrozenInstanceError` if an attempt is made to modify its attributes after
    creation. This ensures the `Config` class behaves as a frozen dataclass,
    enforcing immutability.

    :raises FrozenInstanceError: Raised when attempting to modify a frozen
        instance attribute.
    """
    cfg = Config(
        src=Path("src"),
        dst=Path("dst"),
        sub_dir=False,
        hash="sha256",
        mv=False,
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=False,
        fil_empty=False,
        safe=True,
        debug=False,
    )

    with pytest.raises(FrozenInstanceError):
        cfg.src = Path("other")


def test_config_equality_and_hash():
    """
    Tests the equality and hash functionality of the `Config` class instances to ensure consistent
    behavior when comparing and hashing objects created with the same or different configurations.

    This test ensures:
    - Instances of `Config` with identical attributes are considered equal.
    - The same hash value is produced for `Config` instances with identical attributes.
    - Instances of `Config` with different attributes are not considered equal.
    - Different hash values are produced for `Config` instances with different attributes.
    """
    common_kwargs = dict(
        src=Path("src"),
        dst=Path("dst"),
        sub_dir=False,
        hash="sha256",
        mv=False,
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=False,
        fil_empty=False,
        safe=True,
        debug=False,
    )

    cfg1 = Config(**common_kwargs)
    cfg2 = Config(**common_kwargs)
    cfg3 = Config(**{**common_kwargs, "debug": True})

    assert cfg1 == cfg2
    assert hash(cfg1) == hash(cfg2)

    assert cfg1 != cfg3
