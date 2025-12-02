import logging
from pathlib import Path
from typing import List, Dict, Any

import pytest

import zah.main as main_mod
from zah.config import Config


# ----------------------------------------------------------------------------------------------------------------------
# Helper utilities
# ----------------------------------------------------------------------------------------------------------------------


def make_config(
    src: Path,
    dst: Path,
    sub_dir: bool = False,
    hash_alg: str = "sha3_256",
    mv: bool = False,
    cpy: Path | None = None,
    fil_zip: bool = False,
    fil_cpy: bool = False,
    fil_mv: bool = False,
    fil_empty: bool = False,
    safe: bool = True,
    debug: bool = False,
) -> Config:
    """
    Creates a configuration object for file processing operations including options for
    handling directories, file copying, moving, hashing, and debugging. This function
    facilitates the setup of parameters for specific file handling logic.

    Arguments:
        src (Path): The source path where the files are located.
        dst (Path): The destination path where the processed files will be stored.
        sub_dir (bool): A flag indicating whether to include subdirectories in the
            operation. Defaults to False.
        hash_alg (str): The algorithm to use for file hashing. Defaults to "sha3_256".
        mv (bool): A flag indicating whether to move files instead of copying them.
            Defaults to False.
        cpy (Path | None): An optional path for copied files. Defaults to None.
        fil_zip (bool): A flag indicating whether to handle zipped files. Defaults to False.
        fil_cpy (bool): A flag indicating whether to explicitly enable file copying.
            Defaults to False.
        fil_mv (bool): A flag indicating whether to explicitly enable file moving.
            Defaults to False.
        fil_empty (bool): A flag indicating whether to process empty directories.
            Defaults to False.
        safe (bool): A flag indicating whether to enable safe mode for operations.
            Defaults to True.
        debug (bool): A flag indicating whether to enable debugging. Defaults to False.

    Returns:
        Config: An object containing the specified configuration for file processing.
    """
    return Config(
        src=src,
        dst=dst,
        sub_dir=sub_dir,
        hash=hash_alg,
        mv=mv,
        cpy=cpy,
        fil_zip=fil_zip,
        fil_cpy=fil_cpy,
        fil_mv=fil_mv,
        fil_empty=fil_empty,
        safe=safe,
        debug=debug,
    )


# ----------------------------------------------------------------------------------------------------------------------
# Tests for init()
# ----------------------------------------------------------------------------------------------------------------------


def test_init_with_copy_dir_and_unsafe_and_debug(tmp_path, monkeypatch):
    """
    This function tests the `init` function in the `main_mod` module to verify its behavior
    when parsing command-line arguments, setting up logging, and populating global configuration
    variables. It ensures that the `init` function correctly handles various flags, paths,
    and optional arguments.

    Parameters:
    - tmp_path (Path): Temporary path fixture provided by pytest, used for creating test directories.
    - monkeypatch (MonkeyPatch): Monkeypatch fixture provided by pytest, used for safely patching
      and overriding attributes or methods during testing.

    Raises:
    - AssertionError: If any verification of the `init` function behavior fails.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    cpy = tmp_path / "cpy"

    argv = [
        str(src),
        str(dst),
        "--sub",
        "--hash",
        "sha256",
        "--mv",
        "--cpy",
        str(cpy),
        "--fzip",
        "--fcpy",
        "--fmv",
        "--fmpt",
        "--unsafe",
        "--debug",
        "--unknown-flag",  # should go into parse_known_args' unknown list
    ]

    # Spy on setup_logging to ensure it is called with debug=True and proper log file
    called: dict = {}

    def fake_setup_logging(debug: bool, log_file: str | None = None) -> None:
        called["debug"] = debug
        called["log_file"] = log_file

    monkeypatch.setattr(main_mod, "setup_logging", fake_setup_logging)

    main_mod.init(argv)

    # Check setup_logging call
    assert called["debug"] is True
    assert called["log_file"] == f"{main_mod.script_name}.log"

    # Global logger must be set
    assert main_mod.log is not None
    assert isinstance(main_mod.log, logging.Logger)
    assert main_mod.log.name == main_mod.script_name

    # Global config must be populated according to argv
    cfg = main_mod.config
    assert cfg.src == src
    assert cfg.dst == dst
    assert cfg.sub_dir is True
    assert cfg.hash == "sha256"
    assert cfg.mv is True
    assert cfg.cpy == cpy
    assert cfg.fil_zip is True
    assert cfg.fil_cpy is True
    assert cfg.fil_mv is True
    assert cfg.fil_empty is True
    # unsafe flag inverts safe
    assert cfg.safe is False
    assert cfg.debug is True


def test_init_without_copy_dir_and_safe_default(tmp_path, monkeypatch):
    """
    Tests the initialization behavior of the `main_mod.init` function when called without
    specific flags for copying, safe mode, or debugging. Validates that defaults are applied
    and configuration is correctly set.

    Raises:
        AssertionError: If the test conditions are not met.

    Parameters:
        tmp_path (Path): A temporary directory provided by pytest for testing.
        monkeypatch (pytest.MonkeyPatch): Utility to modify or replace attributes and methods
            during the test runtime.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"

    argv = [
        str(src),
        str(dst),
        # no --cpy, no --unsafe, no --debug
    ]

    # Use real setup_logging but spy on call arguments
    called: dict = {}

    real_setup_logging = main_mod.setup_logging

    def spy_setup_logging(debug: bool, log_file: str | None = None) -> None:
        called["debug"] = debug
        called["log_file"] = log_file
        real_setup_logging(debug, log_file)

    monkeypatch.setattr(main_mod, "setup_logging", spy_setup_logging)

    main_mod.init(argv)

    cfg = main_mod.config
    assert cfg.src == src
    assert cfg.dst == dst
    assert cfg.cpy is None
    assert cfg.sub_dir is False
    assert cfg.safe is True
    assert cfg.debug is False

    assert called["debug"] is False
    assert called["log_file"] == f"{main_mod.script_name}.log"


# ----------------------------------------------------------------------------------------------------------------------
# Tests for run()
# ----------------------------------------------------------------------------------------------------------------------


def test_run_basic_flow_no_subdir_no_copy_no_move(tmp_path, monkeypatch):
    """
    Test the functionality of the `main_mod.run` method where the source directory contains subdirectories,
    but no subdirectories are maintained in the destination, no copy or move operations are performed, and
    only zipping of eligible directories is conducted. The test verifies that appropriate methods are called,
    the outcomes of these calls are as expected, and the resultant `hashes.txt` file contains correct entries.

    Sections:
        - Args
        - Asserts

    Args:
        tmp_path (Path): Pytest fixture to create temporary directories and files for the test.
        monkeypatch (pytest.MonkeyPatch): Fixture used to replace parts of the code with controlled test doubles.

    Asserts:
        Ensures that:
            - The `check_paths` function is called for validating paths.
            - Subdirectories are correctly identified.
            - The `zip_directory` function is called twice for each subdirectory.
            - Only one subdirectory produces a zip file.
            - The `hashes.txt` file is correctly written in the destination directory, containing valid hash entries for the zip.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    # Create some subdirectories under src
    sub_a = src / "A"
    sub_b = src / "B"
    sub_a.mkdir()
    sub_b.mkdir()

    # Prepare global config and logger
    main_mod.config = make_config(
        src=src,
        dst=dst,
        sub_dir=False,
        hash_alg="sha3_256",
        mv=False,
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=False,
        safe=True,
        debug=False,
    )
    main_mod.log = logging.getLogger("test_main_basic")

    # Patch collaborators to avoid heavy I/O
    called = {"check_paths": False, "zip_calls": []}

    def fake_check_paths(src_path, dst_path, cpy_path):
        called["check_paths"] = True
        assert src_path == src
        assert dst_path == dst
        assert cpy_path is None

    def fake_get_subdirectories(root: Path) -> List[Path]:
        assert root == src
        return [sub_a, sub_b]

    def fake_zip_directory(src_dir: Path, dst_dir: Path, allowed, filter_empty: bool) -> tuple[Path | None, int]:
        # Only one directory will produce a zip, the other returns (None, 0)
        called["zip_calls"].append((src_dir, dst_dir, allowed, filter_empty))
        if src_dir == sub_a:
            return dst_dir / f"{src_dir.name}.zip", 5
        return None, 0

    def fake_hash_file(path: Path, algorithm: str) -> str:
        return f"hash-{path.name}-{algorithm}"

    def fake_copy_filtered(src_dir: Path, dst_dir: Path, allowed) -> bool:
        raise AssertionError("copy_filtered should not be called in this scenario") # pragma: no cover

    def fake_clear_folder(path: Path) -> None:
        raise AssertionError("clear_folder should not be called when mv=False") # pragma: no cover

    monkeypatch.setattr(main_mod, "check_paths", fake_check_paths)
    monkeypatch.setattr(main_mod, "get_subdirectories", fake_get_subdirectories)
    monkeypatch.setattr(main_mod, "zip_directory", fake_zip_directory)
    monkeypatch.setattr(main_mod, "hash_file", fake_hash_file)
    monkeypatch.setattr(main_mod, "copy_filtered", fake_copy_filtered)
    monkeypatch.setattr(main_mod, "clear_folder", fake_clear_folder)
    monkeypatch.setattr("builtins.input", lambda prompt="": "")  # final "Press ENTER to exit..."

    main_mod.run()

    assert called["check_paths"] is True
    # Two zip attempts
    assert len(called["zip_calls"]) == 2

    # hashes.txt must exist in dst and contain only the zip that was created
    hashes_file = dst / "hashes.txt"
    assert hashes_file.is_file()
    content = hashes_file.read_text(encoding="utf-8").strip().splitlines()
    # Only sub_a produced a zip
    assert any("A.zip" in line for line in content)
    assert all("B.zip" not in line for line in content)


def test_run_with_subdir_copy_and_move_safe_ok(tmp_path, monkeypatch):
    """
    Test the run functionality with subdirectories for a safe copy-and-move scenario.

    This test ensures that the `run` function in the target module behaves correctly
    when processing subdirectories in a "safe" mode. The test simulates the setup of
    source, destination, and copy directories, mocks necessary helper functions and
    methods, and validates that the sequence of operations (zipping, copying, clearing)
    is executed correctly under the provided configuration.

    Parameters:
        tmp_path (Path): Temporary directory path provided by pytest for storage of test artifacts.
        monkeypatch (pytest.MonkeyPatch): A pytest utility for safely patching attributes for the test scope.

    Raises:
        AssertionError: Raised in case of failed assertions during the test setup or validation.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    cpy = tmp_path / "cpy"
    src.mkdir()
    dst.mkdir()
    cpy.mkdir()

    sub_src = src / "S1"
    sub_src.mkdir()

    main_mod.config = make_config(
        src=src,
        dst=dst,
        sub_dir=True,
        hash_alg="sha3_256",
        mv=True,
        cpy=cpy,
        fil_zip=True,
        fil_cpy=True,
        fil_mv=True,
        fil_empty=True,
        safe=True,
        debug=False,
    )
    main_mod.log = logging.getLogger("test_main_sub_copy_move")

    # Fakes and spies
    def fake_check_paths(src_path, dst_path, cpy_path):
        assert src_path == src
        assert dst_path == dst
        assert cpy_path == cpy

    def fake_get_subdirectories(root: Path) -> List[Path]:
        # Both zip phase and move-cleanup phase will use the same list
        assert root == src
        return [sub_src]

    zip_calls: list[tuple[Path, Path, object, bool]] = []

    def fake_zip_directory(src_dir: Path, dest_dir: Path, allowed, filter_empty: bool) -> tuple[Path | None, int]:
        zip_calls.append((src_dir, dest_dir, allowed, filter_empty))
        return dest_dir / f"{src_dir.name}.zip", 3

    def fake_hash_file(path: Path, algorithm: str) -> str:
        return f"h-{path.name}-{algorithm}"

    copy_calls: list[tuple[Path, Path, object]] = []

    def fake_copy_filtered(src_dir: Path, dest_dir: Path, allowed) -> bool:
        copy_calls.append((src_dir, dest_dir, allowed))
        return True

    cleared: list[Path] = []

    def fake_clear_folder(path: Path) -> None:
        cleared.append(path)

    monkeypatch.setattr(main_mod, "check_paths", fake_check_paths)
    monkeypatch.setattr(main_mod, "get_subdirectories", fake_get_subdirectories)
    monkeypatch.setattr(main_mod, "zip_directory", fake_zip_directory)
    monkeypatch.setattr(main_mod, "hash_file", fake_hash_file)
    monkeypatch.setattr(main_mod, "copy_filtered", fake_copy_filtered)
    monkeypatch.setattr(main_mod, "clear_folder", fake_clear_folder)
    monkeypatch.setattr(main_mod.shutil, "copytree", lambda *args, **kwargs: None)

    # Three input calls:
    # 1) subdirectory name
    # 2) safety confirmation
    # 3) final "Press ENTER to exit..."
    inputs = iter(["session1", "Y", ""])

    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    main_mod.run()

    # dst_dir must be updated to include the subdirectory name
    dst_dir = dst / "session1"
    assert dst_dir.is_dir()

    # cpy_dir must exist as well
    cpy_dir = cpy / "session1"
    assert cpy_dir.is_dir()

    # One zip call for the single subdirectory
    assert len(zip_calls) == 1
    assert zip_calls[0][0] == sub_src
    assert zip_calls[0][1] == dst_dir

    # Two copy_filtered calls: one for cpy, one for mv
    assert len(copy_calls) == 2

    # First: copy from src to cpy_dir (filtered copy)
    assert copy_calls[0][0] == src
    assert copy_calls[0][1] == cpy_dir

    # Second: move step uses copy_filtered from src to dst_dir
    assert copy_calls[1][0] == src
    assert copy_calls[1][1] == dst_dir

    # Source subdirectories must have been cleared
    assert cleared == [sub_src]


def test_run_move_with_safe_and_negative_confirmation_raises(tmp_path, monkeypatch):
    """
    Test case for ensuring the handling of the `main_mod.run` function when the safety
    confirmation is set to a negative response ("N"). The test simulates directory
    structures, applies monkeypatching to replace various functions with test-specific
    behaviors, and verifies that the correct workflow is followed, including that no
    folders are cleared when the safe confirmation fails.

    Sections covered include verification of source and destination directory handling,
    subdirectory identification, dummy hashing, and filtering operations. The test confirms
    a `RuntimeError` is raised when safety confirmation is denied.

    Args:
        tmp_path (Path): Built-in pytest fixture to create a temporary directory for the test.
        monkeypatch (pytest.MonkeyPatch): Built-in pytest fixture used for altering
            attributes, methods, or objects during the test scope.

    Raises:
        RuntimeError: Ensured to be raised when the safety confirmation fails with "N".
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    sub_src = src / "S1"
    sub_src.mkdir()

    main_mod.config = make_config(
        src=src,
        dst=dst,
        sub_dir=False,
        hash_alg="sha3_256",
        mv=True,
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=True,
        safe=True,
        debug=False,
    )
    main_mod.log = logging.getLogger("test_main_safe_negative")

    def fake_check_paths(src_path, dst_path, cpy_path):
        assert src_path == src
        assert dst_path == dst
        assert cpy_path is None

    def fake_get_subdirectories(root: Path) -> List[Path]:
        assert root == src
        return [sub_src]

    def fake_zip_directory(src_dir: Path, dst_dir: Path, allowed, filter_empty: bool) -> tuple[Path | None, int]:
        return dst_dir / f"{src_dir.name}.zip", 1

    def fake_hash_file(path: Path, algorithm: str) -> str:
        return "dummy-hash"

    def fake_copy_filtered(src_dir: Path, dst_dir: Path, allowed) -> bool:
        # Used for mv because fil_mv=True
        return True

    def fake_clear_folder(path: Path) -> None:
        # Should not be reached when safe confirmation fails
        raise AssertionError("clear_folder should not be called when confirmation is negative") # pragma: no cover

    monkeypatch.setattr(main_mod, "check_paths", fake_check_paths)
    monkeypatch.setattr(main_mod, "get_subdirectories", fake_get_subdirectories)
    monkeypatch.setattr(main_mod, "zip_directory", fake_zip_directory)
    monkeypatch.setattr(main_mod, "hash_file", fake_hash_file)
    monkeypatch.setattr(main_mod, "copy_filtered", fake_copy_filtered)
    monkeypatch.setattr(main_mod.shutil, "copytree", lambda *args, **kwargs: None)

    # First input is the safety confirmation; function will raise exception before the final "Press ENTER"
    monkeypatch.setattr("builtins.input", lambda prompt="": "N")

    with pytest.raises(RuntimeError):
        main_mod.run()


# ----------------------------------------------------------------------------------------------------------------------
# Tests for main()
# ----------------------------------------------------------------------------------------------------------------------


class DummySingleInstance:
    """
    Class DummySingleInstance.

    This class is a context manager that tracks its usage by setting flags indicating
    whether it has entered or exited the context. The primary purpose is to check the
    orderly execution of entering and exiting a context without suppressing exceptions
    raised within the managed block. It ensures that resources or states are consistently
    handled across different usages.
    """

    def __init__(self, name: str):
        self.name = name
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True
        # Do not suppress exceptions
        return False


def test_main_success(monkeypatch):
    """
    Tests the main function's successful execution by mocking dependencies.

    The function uses the MonkeyPatch utility to replace certain dependencies of
    the main module with mock objects or behaviors. It ensures that the `main()`
    function initializes correctly, passes arguments correctly, and successfully
    executes its run process.

    Args:
        monkeypatch (pytest.MonkeyPatch): Provides a mechanism to safely replace
        and restore attributes, functions, or objects for controlled test
        behavior.

    Raises:
        AssertionError: If expected outcomes of `init()` and `run()` are not met.
    """
    called: Dict[str, Any] = {"init_argv": None, "run_called": False}

    def fake_init(argv):
        called["init_argv"] = list(argv)

    def fake_run():
        called["run_called"] = True

    monkeypatch.setattr(main_mod, "SingleInstance", DummySingleInstance)
    monkeypatch.setattr(main_mod, "init", fake_init)
    monkeypatch.setattr(main_mod, "run", fake_run)
    monkeypatch.setattr(main_mod.sys, "argv", ["zipandhash", "arg1", "arg2"])

    # Ensure log is set so that potential errors would be logged, not re-raised
    main_mod.log = logging.getLogger("test_main_entry_ok")

    main_mod.main()

    assert called["init_argv"] == ["arg1", "arg2"]
    assert called["run_called"] is True


def test_main_logs_error_when_logger_present(monkeypatch, caplog):
    """
    Tests the logging behavior of the main function when an exception occurs during
    execution, ensuring that an error message is logged and the exception does not
    propagate to the caller.

    This function temporarily modifies system attributes and functions using
    monkeypatch to simulate specific behaviors and scenarios. Additionally, it
    checks that the logger captures the appropriate error messages.

    Parameters:
    monkeypatch: _pytest.monkeypatch.MonkeyPatch
        Utility to patch functions, methods, attributes, or other objects for testing.

    caplog: _pytest.logging.LogCaptureFixture
        Fixture to capture log messages for assertions.
    """
    def fake_init(argv):
        # No-op
        pass

    def fake_run():
        raise RuntimeError("run failure")

    monkeypatch.setattr(main_mod, "SingleInstance", DummySingleInstance)
    monkeypatch.setattr(main_mod, "init", fake_init)
    monkeypatch.setattr(main_mod, "run", fake_run)

    logger = logging.getLogger("test_main_entry_error_log")
    main_mod.log = logger

    monkeypatch.setattr(main_mod.sys, "argv", ["zipandhash"])

    with caplog.at_level(logging.ERROR, logger=logger.name):
        main_mod.main()

    # Error must have been logged, and exception must not propagate
    messages = [record.getMessage() for record in caplog.records]
    assert any("run failure" in msg for msg in messages)


def test_main_reraises_error_when_logger_none(monkeypatch):
    """
    Tests that the `main` function properly re-raises an exception when the logger
    is not initialized.

    The test replaces key components of the `main` function with mock
    implementations using `monkeypatch`. Specifically, it mocks the `SingleInstance`
    class, initialization function, and runtime execution function to simulate
    a scenario where a `ValueError` is raised. The purpose of this test is to ensure
    that errors occurring during runtime are not silently suppressed when the
    logger object is set to `None`.

    Parameters:
        monkeypatch (pytest.MonkeyPatch): A pytest fixture for dynamically
            modifying or replacing attributes and functions during the test.

    Raises:
        ValueError: Confirms that the `ValueError` exception raised in the mocked
            `run` function is correctly re-raised by the `main` function.
    """
    def fake_init(argv):
        # No-op
        pass

    def fake_run():
        raise ValueError("boom")

    monkeypatch.setattr(main_mod, "SingleInstance", DummySingleInstance)
    monkeypatch.setattr(main_mod, "init", fake_init)
    monkeypatch.setattr(main_mod, "run", fake_run)
    monkeypatch.setattr(main_mod.sys, "argv", ["zipandhash"])

    main_mod.log = None

    with pytest.raises(ValueError):
        main_mod.main()


def test_run_with_copy_without_filter_uses_copytree_only(tmp_path, monkeypatch):
    """
    Tests the behavior of the `run` function in scenarios involving the use of `shutil.copytree`
    without a filter phase. Ensures that the correct setup, operations, and validations are
    performed according to the given configuration.

    This test mock-patches various functions and attributes to simulate specific behaviors
    and conditions during execution. It checks that appropriate functions are called or
    not called, depending on the configuration, and verifies the correctness of the
    outcomes and side effects such as copied directories and generated files.

    Attributes
    ----------
    tmp_path : Path
        Temporary directory created for tests. Provided by pytest fixtures.
    monkeypatch : MonkeyPatch
        Used to dynamically modify or replace parts of the system under test.

    Raises
    ------
    AssertionError
        If any mock function not expected to be called in this test scenario is invoked.
        If expected conditions or assertions in the test case are violated.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    cpy = tmp_path / "cpy"
    src.mkdir()
    dst.mkdir()
    cpy.mkdir()

    sub_src = src / "S1"
    sub_src.mkdir()

    main_mod.config = make_config(
        src=src,
        dst=dst,
        sub_dir=False,
        hash_alg="sha3_256",
        mv=False,         # no move phase
        cpy=cpy,
        fil_zip=False,
        fil_cpy=False,    # branch without filter
        fil_mv=False,
        fil_empty=False,
        safe=True,
        debug=False,
    )
    main_mod.log = logging.getLogger("test_main_copy_no_filter")

    def fake_check_paths(src_path, dst_path, cpy_path):
        assert src_path == src
        assert dst_path == dst
        assert cpy_path == cpy

    def fake_get_subdirectories(root: Path) -> List[Path]:
        # Used both in zip phase and move-cleanup phase (here mv=False so only first)
        assert root == src
        return [sub_src]

    def fake_zip_directory(src_dir: Path, dst_dir: Path, allowed, filter_empty) -> tuple[Path | None, int]:
        # Ensure zip phase still runs: we need at least one zip for hashes.txt
        return dst_dir / f"{src_dir.name}.zip", 1

    def fake_hash_file(path: Path, algorithm: str) -> str:
        return f"hash-{path.name}-{algorithm}"

    def fake_copy_filtered(src_dir: Path, dest_dir: Path, allowed) -> bool:
        # Must not be called when fil_cpy=False and fil_mv=False
        raise AssertionError("copy_filtered must not be called when fil_cpy=False and fil_mv=False") # pragma: no cover

    copytree_calls: list[tuple[Path, Path]] = []

    def fake_copytree(src_dir: Path, dest_dir: Path, dirs_exist_ok: bool = False):
        copytree_calls.append((src_dir, dest_dir))

    def fake_clear_folder(path: Path) -> None:
        # mv=False, so clear_folder should never be called
        raise AssertionError("clear_folder must not be called when mv=False") # pragma: no cover

    monkeypatch.setattr(main_mod, "check_paths", fake_check_paths)
    monkeypatch.setattr(main_mod, "get_subdirectories", fake_get_subdirectories)
    monkeypatch.setattr(main_mod, "zip_directory", fake_zip_directory)
    monkeypatch.setattr(main_mod, "hash_file", fake_hash_file)
    monkeypatch.setattr(main_mod, "copy_filtered", fake_copy_filtered)
    monkeypatch.setattr(main_mod, "clear_folder", fake_clear_folder)
    monkeypatch.setattr(main_mod.shutil, "copytree", fake_copytree)
    monkeypatch.setattr("builtins.input", lambda prompt="": "")  # final "Press ENTER to exit..."

    main_mod.run()

    # hashes.txt must exist in dst
    hashes_file = dst / "hashes.txt"
    assert hashes_file.is_file()

    # Two copytree calls expected in copy phase:
    # 1) dst_dir -> cpy_dir
    # 2) src -> cpy_dir (because fil_cpy=False)
    cpy_dir = cpy  # no sub_dir here
    assert len(copytree_calls) == 2
    assert (dst, cpy_dir) in copytree_calls
    assert (src, cpy_dir) in copytree_calls


def test_run_with_move_without_filter_uses_copytree(tmp_path, monkeypatch):
    """
    Test that `run` function operates correctly when moving files without applying filters.

    This test verifies the behavior of the `run` function when the `mv` (move) feature is
    enabled and file filtering (`fil_mv`) is disabled. Specifically, it ensures that the
    `copytree` operation is applied and no filtered copying branches are executed. The setup
    also includes initialization of source and destination directories, mocks for required
    methods, and validation of expected operations.

    Parameters:
        tmp_path (Path): Temporary directory path for creating source and destination directories.
        monkeypatch: Fixture for safely modifying or replacing parts of the code during the test.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()
    dst.mkdir()

    sub_src = src / "S1"
    sub_src.mkdir()

    main_mod.config = make_config(
        src=src,
        dst=dst,
        sub_dir=False,
        hash_alg="sha3_256",
        mv=True,          # mv enabled
        cpy=None,
        fil_zip=False,
        fil_cpy=False,
        fil_mv=False,     # branch without filter for mv
        fil_empty=False,
        safe=False,
        debug=False,
    )
    main_mod.log = logging.getLogger("test_main_move_no_filter")

    def fake_check_paths(src_path, dst_path, cpy_path):
        assert src_path == src
        assert dst_path == dst
        assert cpy_path is None

    def fake_get_subdirectories(root: Path) -> List[Path]:
        # Used both in zip phase and in move-cleanup phase
        assert root == src
        return [sub_src]

    def fake_zip_directory(src_dir: Path, dst_dir: Path, allowed, filter_empty: bool) -> tuple[Path | None, int]:
        return dst_dir / f"{src_dir.name}.zip", 1

    def fake_hash_file(path: Path, algorithm: str) -> str:
        return f"h-{path.name}-{algorithm}"

    def fake_copy_filtered(src_dir: Path, dest_dir: Path, allowed) -> bool:
        # For mv we expect the non-filter branch (copytree) when fil_mv=False
        raise AssertionError("copy_filtered must not be called when fil_mv=False") # pragma: no cover

    copytree_calls: list[tuple[Path, Path]] = []
    cleared: list[Path] = []

    def fake_copytree(src_dir: Path, dest_dir: Path, dirs_exist_ok: bool = False):
        copytree_calls.append((src_dir, dest_dir))

    def fake_clear_folder(path: Path) -> None:
        cleared.append(path)

    monkeypatch.setattr(main_mod, "check_paths", fake_check_paths)
    monkeypatch.setattr(main_mod, "get_subdirectories", fake_get_subdirectories)
    monkeypatch.setattr(main_mod, "zip_directory", fake_zip_directory)
    monkeypatch.setattr(main_mod, "hash_file", fake_hash_file)
    monkeypatch.setattr(main_mod, "copy_filtered", fake_copy_filtered)
    monkeypatch.setattr(main_mod, "clear_folder", fake_clear_folder)
    monkeypatch.setattr(main_mod.shutil, "copytree", fake_copytree)

    # Two input calls:
    # 1) safety confirmation
    # 2) final "Press ENTER to exit..."
    inputs = iter(["Y", ""])
    monkeypatch.setattr("builtins.input", lambda prompt="": next(inputs))

    main_mod.run()

    # hashes.txt must exist
    hashes_file = dst / "hashes.txt"
    assert hashes_file.is_file()

    # For mv with fil_mv=False we expect one copytree from src to dst
    assert (src, dst) in copytree_calls

    # Source subdirectories must have been cleared
    assert cleared == [sub_src]
