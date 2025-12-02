import runpy

import pytest

import zah.main as main_mod


def test_package_entrypoint_invokes_main(monkeypatch):
    """
    Test that the package entry point calls the `main` function properly.

    This function ensures that when the module is executed as a script,
    the `main` function within the module is invoked and its behavior
    is correctly simulated and validated.

    Parameters:
        monkeypatch: pytest.MonkeyPatch
            A fixture that allows dynamic modification of code at runtime.

    Raises:
        SystemExit: This is raised when `runpy.run_module` is executed,
        as it mimics the behavior of a script's execution causing an
        exit in the runtime.

    Returns:
        None
    """
    called = {"called": False}

    def fake_main() -> int:
        called["called"] = True
        return 0

    monkeypatch.setattr(main_mod, "main", fake_main)

    # Simulate: python -m zah  -> executes zah.__main__ with __name__ == "__main__"
    with pytest.raises(SystemExit) as excinfo:
        runpy.run_module("zah.__main__", run_name="__main__")

    # SystemExit code must match fake_main() return value
    assert excinfo.value.code == 0
    assert called["called"] is True
