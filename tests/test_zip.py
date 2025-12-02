import zipfile

from zah.zip import zip_directory


def test_zip_directory_with_filter_includes_only_allowed_extensions(tmp_path):
    """
    Tests the `zip_directory` function to ensure it correctly includes only files with the allowed
    extensions while creating a zip archive and counts the included files accurately.

    :param tmp_path: Temporary directory provided by pytest for creating and manipulating
                     test files and directories.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src_dir = tmp_path / "src"
    dst_dir = tmp_path / "dst"
    src_dir.mkdir()
    dst_dir.mkdir()

    # Top-level files
    f1 = src_dir / "file1.txt"
    f2 = src_dir / "file2.TXT"   # upper-case extension, should match thanks to .lower()
    f3 = src_dir / "file3.bin"   # should be excluded
    f1.write_text("content 1")
    f2.write_text("content 2")
    f3.write_text("content 3")

    # Nested directory
    sub = src_dir / "sub"
    sub.mkdir()
    f4 = sub / "nested.md"
    f4.write_text("nested content")

    allowed_ext = {".txt", ".md"}

    zip_path, count = zip_directory(src_dir, dst_dir, allowed_ext)

    assert zip_path is not None
    assert zip_path.parent == dst_dir
    assert zip_path.name == src_dir.name + ".zip"
    # 3 files: file1.txt, file2.TXT, sub/nested.md
    assert count == 3

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

    # Zip uses forward slashes for internal paths
    assert "file1.txt" in names
    assert "file2.TXT" in names
    assert "sub/nested.md" in names
    assert "file3.bin" not in names


def test_zip_directory_without_filter_includes_all_files(tmp_path):
    """
    Tests the behavior of the `zip_directory` function when no file filter is applied,
    ensuring that all files within the source directory, regardless of extension, are
    included in the resulting zip file.

    :param tmp_path: Temporary path fixture provided by the test framework.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src_dir = tmp_path / "src_all"
    dst_dir = tmp_path / "dst_all"
    src_dir.mkdir()
    dst_dir.mkdir()

    (src_dir / "a.txt").write_text("a")
    (src_dir / "b.bin").write_text("b")
    sub = src_dir / "sub"
    sub.mkdir()
    (sub / "c.md").write_text("c")

    zip_path, count = zip_directory(src_dir, dst_dir, allowed_ext=set())

    assert zip_path is not None
    # 3 files total
    assert count == 3

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = set(zf.namelist())

    assert names == {"a.txt", "b.bin", "sub/c.md"}


def test_zip_directory_with_filter_and_no_matching_files_returns_none(tmp_path):
    """
    Tests the behavior of the `zip_directory` function when no files match the provided
    allowed extensions.

    This test verifies that when no files with allowed extensions exist in the source
    directory, the function should return `None` as the zip path and a file count of 0.
    Additionally, it ensures that no zip archive is created in the destination directory.

    :param tmp_path: Temporary directory path for the test.
    :type tmp_path: pathlib.Path
    :return: None
    """
    src_dir = tmp_path / "src_none"
    dst_dir = tmp_path / "dst_none"
    src_dir.mkdir()
    dst_dir.mkdir()

    # Only .txt files present
    (src_dir / "only.txt").write_text("data")

    allowed_ext = {".xyz"}  # No match

    zip_path, count = zip_directory(src_dir, dst_dir, allowed_ext, True)

    assert zip_path is None
    assert count == 0

    # The expected archive name must not exist on disk
    expected_zip = (dst_dir / src_dir.name).with_suffix(".zip")
    assert not expected_zip.exists()

    zip_path, count = zip_directory(src_dir, dst_dir, allowed_ext)

    assert zip_path is not None
    assert count == 0

    # The expected archive name must exist on disk
    expected_zip = (dst_dir / src_dir.name).with_suffix(".zip")
    assert expected_zip.exists()
