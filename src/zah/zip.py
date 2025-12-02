import os
import zipfile
from pathlib import Path
from typing import Tuple, List, Optional, Set


__all__ = ["zip_directory"]


def zip_directory(src_dir: Path, dst_dir: Path, allowed_ext: Set[str],
                  filter_empty: bool = False) -> Tuple[Optional[Path], int]:
    """
    Zips files from the source directory into a zip archive located in the destination
    directory. Only files with extensions present in the allowed_ext set are included
    in the archive. If allowed_ext is empty, all files in the source directory are zipped.

    :param src_dir: Path of the source directory to zip
    :type src_dir: Path
    :param dst_dir: Path where the resulting zip archive will be stored
    :type dst_dir: Path
    :param allowed_ext: Allowed file extensions to include in the zip archive. Should be
        a set of lowercase file extensions (e.g., {'.txt', '.jpg'}); if empty, all files will be included
    :type allowed_ext: Set[str]
    :param filter_empty: Flag indicating whether to filter out empty zip archives after processing
    :type filter_empty: bool
    :return: A tuple containing the path to the created zip archive or None if no files
        were zipped, and the number of files included in the archive
    :rtype: Tuple[Optional[Path], int]
    """
    dst_zip = (dst_dir / src_dir.name).with_suffix(".zip")

    files_to_zip: List[Path] = []
    for root, _, files in os.walk(src_dir):
        root_path = Path(root)
        for f in files:
            file_path = root_path / f
            if not allowed_ext or file_path.suffix.lower() in allowed_ext:
                files_to_zip.append(file_path)

    if filter_empty and not files_to_zip:
        return None, 0

    with zipfile.ZipFile(dst_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in files_to_zip:
            arcname = file_path.relative_to(src_dir)
            zf.write(file_path, arcname)

    return dst_zip, len(files_to_zip)

