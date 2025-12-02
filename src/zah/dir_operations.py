import os
import shutil
from pathlib import Path
from typing import List, Optional, Set


__all__ = ["check_paths", "get_subdirectories", "clear_folder", "copy_filtered"]


def check_paths(src: Path, dst: Path, cpy: Optional[Path] = None):
    """
    Check the existence and validity of the provided source, destination, and optional copy paths.
    Ensures that the directories exist and are valid directories. If the directories do not exist,
    it will create the destination and optional copy directories. Raises exceptions when the
    source does not exist or any of the paths are not directories.

    :param src: A Path object indicating the source directory.
    :param dst: A Path object indicating the destination directory.
                Will be created if it doesn't exist.
    :param cpy: An optional Path object indicating the copy directory.
                Will be created if it doesn't exist.
    :return: None
    :raises FileNotFoundError: If the source directory does not exist.
    :raises NotADirectoryError: If any provided path is not a directory.
    """
    if not src.exists():
        raise FileNotFoundError(f"Source directory {src} does not exist")
    dst.mkdir(parents=True, exist_ok=True)
    if cpy:
        cpy.mkdir(parents=True, exist_ok=True)
    if not src.is_dir():
        raise NotADirectoryError(f"Source directory {src} is not a directory")
    if not dst.is_dir():
        raise NotADirectoryError(f"Destination directory {dst} is not a directory")
    if cpy and not cpy.is_dir():
        raise NotADirectoryError(f"Copy directory {cpy} is not a directory")


def get_subdirectories(path_dir: Path) -> List[Path]:
    """
    Returns a list of subdirectories within the specified directory.

    This function takes a given directory path and retrieves all its
    immediate subdirectories.

    :param path_dir: The directory path where the subdirectories will be
        listed.
    :type path_dir: Path
    :return: A list of paths corresponding to subdirectories within the
        specified directory.
    :rtype: List[Path]
    """
    return [d for d in path_dir.iterdir() if d.is_dir()]


def clear_folder(path_dir: Path):
    """
    Removes all files and subdirectories within a specified directory.

    This function clears the contents of the provided directory by deleting
    all files, symbolic links, and subdirectories within it. It does not
    remove the directory itself. If the directory contains nested
    subdirectories, they are removed recursively.

    :param path_dir: The path to the directory whose contents should be deleted.
    :type path_dir: Path
    :return: None
    """
    for name in os.listdir(path_dir):
        full_path = os.path.join(path_dir, name)
        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.unlink(full_path)
        elif os.path.isdir(full_path):  # pragma: no cover
            shutil.rmtree(full_path)


def copy_filtered(src: Path, dst: Path, allowed_ext: Set[str]) -> bool:
    """
    Recursively copies files from a source directory to a destination directory, filtering
    them based on a set of allowed file extensions.

    This function iterates over the source directory, copying only files that have extensions
    contained in the `allowed_ext` set to the destination directory. If the function
    encounters a subdirectory, it recursively processes that subdirectory. Empty directories
    in the destination are removed if they do not contain any files matching the filter.

    :param src: Path to the source directory.
    :type src: Path
    :param dst: Path to the destination directory.
    :type dst: Path
    :param allowed_ext: A set of allowed file extensions (case-insensitive).
    :type allowed_ext: Set[str]
    :return: True if any valid files are copied; False otherwise.
    :rtype: bool
    """
    has_valid_files = False
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        dst_item = dst / item.name

        if item.is_file():
            if item.suffix.lower() in allowed_ext:
                shutil.copy2(item, dst_item)
                has_valid_files = True

        elif item.is_dir(): # pragma: no cover
            sub_has_files = copy_filtered(item, dst_item, allowed_ext)

            if not sub_has_files:
                if dst_item.exists():   # pragma: no cover
                    dst_item.rmdir()
            else:
                has_valid_files = True

    return has_valid_files
