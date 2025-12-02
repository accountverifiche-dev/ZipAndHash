from pathlib import Path

import pytest

from zah.single_instance import SingleInstance
import zah.single_instance as si


def test_single_instance_init_sets_lockfile_and_fd_none(tmp_path):
    """
    Tests initialization of a SingleInstance object to ensure that the lockfile
    attribute is set correctly and the file descriptor (`fd`) is set to None.

    Parameters:
        tmp_path (Path): Temporary path fixture provided by the test framework to
                         create temporary directory and files.

    Raises:
        AssertionError: If the lockfile is not set to the expected Path instance,
                        or if `fd` is not set to None.
    """
    lock_path = tmp_path / "my.lock"
    inst = SingleInstance(str(lock_path))

    assert isinstance(inst.lockfile, Path)
    assert inst.lockfile == lock_path
    assert inst.fd is None


def test_single_instance_acquire_and_release_creates_and_removes_lockfile(tmp_path):
    """
    Tests that a single instance of `SingleInstance` can acquire a lock by creating
    a lock file on the filesystem and properly release it by removing the lock file.

    This test checks:
    1. That the lock file is created on the filesystem when the `acquire` method of
       `SingleInstance` is called.
    2. That the lock file is removed from the filesystem when the `release` method
       of `SingleInstance` is called.
    3. Ensures no double-release behavior by not calling `release()` twice, as the
       implementation does not reset the file descriptor to None after closing, which
       would cause issues with subsequent releases on the already closed descriptor.

    Parameters:
        tmp_path (Path): Temporary directory provided by the pytest fixture for creating
        temporary paths and ensuring filesystem integrity during tests.
    """
    lock_path = tmp_path / "proc.lock"
    inst = SingleInstance(str(lock_path))

    # Real acquisition on filesystem
    inst.acquire()
    assert inst.fd is not None
    assert lock_path.exists()

    # Real release
    inst.release()
    assert not lock_path.exists()
    # Do not call release() twice: the implementation does not reset fd to None
    # after closing, so a second call would try to close an already closed fd.



def test_single_instance_release_without_acquire_is_noop(tmp_path):
    """
    Tests the behavior of the `release` method in the `SingleInstance` class when it is
    called without a prior `acquire` call, ensuring it performs no operation.

    Parameters:
    tmp_path: Path
        A temporary file path fixture, provided by the testing framework, used to
        create a unique temporary directory for testing.

    Raises:
    AssertionError
        If the lock file unexpectedly exists after calling `release`.
    """
    lock_path = tmp_path / "no_acquire.lock"
    inst = SingleInstance(str(lock_path))

    # fd is None, no file exists
    inst.release()
    assert not lock_path.exists()


def test_single_instance_retries_on_existing_lock_and_eventually_succeeds(monkeypatch, capsys, tmp_path):
    """
    Tests the behavior of the `SingleInstance` class when retrying lock acquisition
    due to an existing lock, and verifies that it eventually succeeds.

    This test simulates a scenario where the first attempt to acquire a lock fails
    due to the existence of a lock (emulated by raising `FileExistsError`), while
    subsequent attempts succeed. It confirms the correct handling of retries and
    expected side effects such as informational messages and cleanup.

    Parameters:
    monkeypatch: pytest.MonkeyPatch
        Fixture provided by pytest to alter/replace attributes or methods during
        testing.
    capsys: pytest.CaptureFixture
        Fixture provided by pytest for capturing stdout and stderr during tests.
    tmp_path: pathlib.Path
        Fixture provided by pytest for creating temporary directories unique to
        the test.

    Raises:
    FileExistsError: The exception is deliberately raised by the fake `open()`
    function to simulate testing the lock retry mechanism.
    """
    lock_path = tmp_path / "retry.lock"
    inst = SingleInstance(str(lock_path))

    call_counter = {"n": 0}

    def fake_open(path, flags):
        # First call -> simulate existing lock; second call -> success
        call_counter["n"] += 1
        assert path == inst.lockfile
        if call_counter["n"] == 1:
            raise FileExistsError
        # Return a dummy fd
        return 123

    def fake_write(fd, data):
        # Simple stub to avoid writing to a real fd
        assert fd == 123
        return len(data)

    # Avoid sleeping in the retry loop
    monkeypatch.setattr(si, "sleep", lambda _: None)
    monkeypatch.setattr(si.os, "open", fake_open)
    monkeypatch.setattr(si.os, "write", fake_write)

    inst.acquire()
    assert call_counter["n"] == 2
    assert inst.fd == 123

    captured = capsys.readouterr()
    # One informational message on first failure
    assert "Process already executing" in captured.err

    # Clean up manually: we did not create a real file
    inst.fd = None


def test_single_instance_acquire_exceeds_max_wait_calls_sys_exit(monkeypatch, tmp_path):
    """
    Tests the behavior of `SingleInstance.acquire` when the acquisition exceeds the
    maximum wait time and ensures that `sys.exit` is called with the appropriate exit code.

    Arguments:
        monkeypatch: pytest's monkeypatch fixture used for dynamically modifying or
            overriding parts of the function during the test.
        tmp_path: pytest fixture that provides a temporary directory unique to the test
            invocation.

    Raises:
        ExitCalled: Exception raised during the test to simulate `sys.exit` being
            called. Captures the exit code.
    """
    lock_path = tmp_path / "timeout.lock"
    inst = SingleInstance(str(lock_path))

    # Force MAX_MINUTES_WAITING to 0 so the first failure reaches the threshold
    monkeypatch.setattr(
        SingleInstance, "_SingleInstance__MAX_MINUTES_WAITING", 0, raising=False
    )

    # os.open always raises FileExistsError to trigger the timeout branch
    def always_failing_open(path, flags):
        raise FileExistsError

    monkeypatch.setattr(si.os, "open", always_failing_open)
    monkeypatch.setattr(si, "sleep", lambda _: None)

    class ExitCalled(Exception):
        def __init__(self, code: int) -> None:
            self.code = code

    def fake_exit(code: int) -> None:
        raise ExitCalled(code)

    monkeypatch.setattr(si.sys, "exit", fake_exit)

    with pytest.raises(ExitCalled) as excinfo:
        inst.acquire()

    assert excinfo.value.code == 1


def test_single_instance_context_manager_creates_and_removes_lockfile(tmp_path):
    """
    Tests the context manager functionality of the SingleInstance class, ensuring
    that it properly creates and removes a lock file.

    The test creates a temporary lock file path and initializes the SingleInstance
    object with it. It validates that the lock file exists and is removed after
    exiting the context manager.

    Parameters:
    tmp_path: Path
        A pytest fixture that provides a temporary directory unique to the test
        invocation.

    Raises:
    AssertionError
        If any assertion regarding the lock file's existence or the behavior of
        the SingleInstance context manager fails.
    """
    lock_path = tmp_path / "ctx.lock"
    inst = SingleInstance(str(lock_path))

    with inst as ctx:
        # __enter__ must return the instance
        assert ctx is inst
        assert inst.fd is not None
        assert lock_path.exists()

    # After leaving the context, the lockfile must be removed
    assert not lock_path.exists()
