import pytest

from zah.dir_operations import check_paths, get_subdirectories, clear_folder, copy_filtered


def test_check_paths_creates_dst_and_cpy(tmp_path):
    """
    Tests the ``check_paths`` function to ensure that it appropriately creates
    the destination and copy directories when provided a source directory.

    The test verifies that the ``check_paths`` function does not raise an
    exception when executed and ensures that the specified directories are
    created as expected.

    :param tmp_path: A temporary filesystem path provided by the pytest fixture.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    cpy = tmp_path / "cpy"

    src.mkdir()

    # Should not raise
    check_paths(src, dst, cpy)

    assert src.is_dir()
    assert dst.is_dir()
    assert cpy.is_dir()


def test_check_paths_raises_when_src_missing(tmp_path):
    """
    Tests that the `check_paths` function raises a `FileNotFoundError` when the
    source path is missing. This ensures the function correctly handles cases when
    the source file or directory does not exist.

    :param tmp_path: Temporary directory for the test, provided by pytest.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src = tmp_path / "missing_src"
    dst = tmp_path / "dst"

    with pytest.raises(FileNotFoundError):
        check_paths(src, dst, None)


def test_check_paths_raises_when_src_is_not_directory(tmp_path):
    """
    Test case for verifying that check_paths raises a NotADirectoryError
    when the source path is not a directory.

    This function creates a temporary file at the source path, writes
    some content to it to simulate a non-directory, and then validates
    that the function under test raises the appropriate exception.

    :param tmp_path: Temporary directory path fixture provided by pytest.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src = tmp_path / "src_file"
    dst = tmp_path / "dst"
    cpy = tmp_path / "cpy"

    src.write_text("not a directory")

    with pytest.raises(NotADirectoryError):
        check_paths(src, dst, cpy)


def test_get_subdirectories_returns_only_directories(tmp_path):
    """
    Tests the functionality of the `get_subdirectories` function to ensure
    it returns only the directories within a given directory path, excluding
    any files.

    :param tmp_path: Temporary directory provided by pytest for creating and
        testing files and directories.
    :type tmp_path: pathlib.Path
    :return: None
    """
    root = tmp_path / "root"
    root.mkdir()

    sub1 = root / "sub1"
    sub2 = root / "sub2"
    file1 = root / "file.txt"

    sub1.mkdir()
    sub2.mkdir()
    file1.write_text("content")

    subs = get_subdirectories(root)
    names = {p.name for p in subs}

    assert names == {"sub1", "sub2"}
    assert file1 not in subs


def test_clear_folder_removes_files_and_subdirectories(tmp_path):
    """
    Tests whether the `clear_folder` function properly removes all files,
    subdirectories, and symbolic links in a specified directory while
    keeping the directory itself intact.

    Given a nested directory structure with files, subdirectories, and
    an optional symlink, this test ensures that the specified directory
    is cleared entirely and emptied without being deleted.

    :param tmp_path: A `Path` object provided by pytest's `tmp_path` fixture
                     to create a temporary directory structure for testing.
    :return: None
    """
    root = tmp_path / "root"
    root.mkdir()

    file1 = root / "file1.txt"
    file1.write_text("content")

    sub = root / "sub"
    sub.mkdir()
    file2 = sub / "file2.txt"
    file2.write_text("more content")

    # Optionally create a symlink to exercise the islink branch, if supported.
    link = root / "symlink"
    try:
        link.symlink_to(file1)
    except (OSError, NotImplementedError):
        # On some platforms (e.g. Windows without admin) symlinks may not be available.
        pass

    clear_folder(root)

    assert root.exists()
    # Directory must be empty after clear_folder
    assert list(root.iterdir()) == []


def test_copy_filtered_copies_only_allowed_extensions_and_prunes_empty_dirs(tmp_path):
    """
    Tests the `copy_filtered` function to ensure it correctly copies files with
    allowed extensions from the source directory to the destination directory.
    The test verifies that files and directories without allowed files or extensions
    are appropriately excluded, and empty directories are pruned.

    :param tmp_path: Temporary directory provided by the pytest framework.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()

    # Top-level files
    allowed_top = src / "file1.TXT"
    disallowed_top = src / "file2.log"
    allowed_top.write_text("allowed")
    disallowed_top.write_text("not allowed")

    # Subdir with allowed file
    sub_with = src / "sub_with"
    sub_with.mkdir()
    nested_allowed = sub_with / "nested.md"
    nested_allowed.write_text("nested allowed")

    # Subdir with no allowed files
    sub_without = src / "sub_without"
    sub_without.mkdir()
    nested_disallowed = sub_without / "note.tmp"
    nested_disallowed.write_text("nested not allowed")

    allowed_ext = {".txt", ".md"}

    result = copy_filtered(src, dst, allowed_ext)
    assert result is True

    # Allowed files must exist in destination
    assert (dst / "file1.TXT").is_file()
    assert (dst / "sub_with" / "nested.md").is_file()

    # Disallowed file must not be copied
    assert not (dst / "file2.log").exists()

    # Subdirectory without allowed files must be pruned
    assert not (dst / "sub_without").exists()


def test_copy_filtered_returns_false_and_creates_empty_dst_when_no_allowed_files(tmp_path):
    """
    Tests that `copy_filtered` correctly returns `False` and creates an empty destination directory
    when no source files match the allowed file extensions.

    :param tmp_path: Temporary directory path created by pytest for testing purposes.
    :return: Test outcome, ensuring the destination directory is empty and no files
             are copied when none of the source files match allowed extensions.
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()

    file1 = src / "a.bin"
    file2 = src / "b.BIN"
    file1.write_text("data 1")
    file2.write_text("data 2")

    sub = src / "sub"
    sub.mkdir()
    file3 = sub / "c.bin"
    file3.write_text("data 3")

    allowed_ext = {".txt"}  # No file will match

    result = copy_filtered(src, dst, allowed_ext)

    assert result is False
    assert dst.is_dir()
    # Destination must be empty: no copied files, and subdirs pruned
    assert list(dst.iterdir()) == []


def test_check_paths_with_none_copy_does_not_fail(tmp_path):
    """
    Tests that the function `check_paths` does not fail when a `None`
    value is passed as the copy argument and ensures the destination
    directory is created.

    :param tmp_path: Temporary path fixture provided by pytest.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.mkdir()

    # This should not raise after fixing check_paths
    check_paths(src, dst, None)

    assert dst.is_dir()


def test_check_paths_raises_when_dst_is_not_directory(tmp_path, monkeypatch):
    """
    Tests that the check_paths function raises a NotADirectoryError when the specified destination (dst)
    is not a directory.

    This test creates a source (src) as a directory and a destination (dst) as a regular file.
    The test uses pytest to verify the expected NotADirectoryError is raised.

    :param tmp_path: A pytest fixture providing a temporary directory unique to the test.
    :param monkeypatch: A pytest fixture used to dynamically modify or mock parts of the code during testing.
    :return: None
    """
    src = tmp_path / "src"
    src.mkdir()

    dst = tmp_path / "dst_file"
    dst.write_text("not a directory")

    # Prevent dst.mkdir() from raising or changing the file
    monkeypatch.setattr("zah.dir_operations.Path.mkdir", lambda self, parents=True, exist_ok=True: None)

    with pytest.raises(NotADirectoryError):
        check_paths(src, dst, None)


def test_check_paths_raises_when_cpy_is_not_directory(tmp_path, monkeypatch):
    """
    Tests the `check_paths` function to ensure it raises a `NotADirectoryError` when
    the `cpy` path is not a directory. The test verifies that the function correctly
    identifies invalid directory structures to prevent unexpected behavior.

    :param tmp_path: Temporary directory provided by pytest for creating test files
        and directories.
    :type tmp_path: pathlib.Path
    :param monkeypatch: Pytest fixture that allows changing or mocking of parts
        of the system under test.
    :type monkeypatch: pytest.MonkeyPatch
    :return: None
    """
    src = tmp_path / "src"
    src.mkdir()

    dst = tmp_path / "dst"
    dst.mkdir()

    cpy = tmp_path / "cpy_file"
    cpy.write_text("not a directory")

    # Neutralize mkdir so that cpy stays a file and no exception is raised before the check
    monkeypatch.setattr("zah.dir_operations.Path.mkdir", lambda self, parents=True, exist_ok=True: None)

    with pytest.raises(NotADirectoryError):
        check_paths(src, dst, cpy)
