from pathlib import Path
from typing import Optional
from dataclasses import dataclass


__all__ = ["Config"]


@dataclass(frozen=True)
class Config:
    """
    Configuration class for managing file processing settings.

    This class defines a set of immutable configurations for managing
    file operations such as copying, moving, and other safe operations.
    It enables fine-tuned control over source/destination paths, file
    handling flags, and debugging options.

    :ivar src: The source path for the files to be processed.
    :type src: Path
    :ivar dst: The destination path for the files to be processed.
    :type dst: Path
    :ivar sub_dir: Indicates whether to process files in subdirectories.
    :type sub_dir: bool
    :ivar hash: The hash algorithm used for processing files.
    :type hash: str
    :ivar mv: Whether the files should be moved after processing.
    :type mv: bool
    :ivar cpy: An optional path for copying files during the operation.
    :type cpy: Optional[Path]
    :ivar fil_zip: Flag to indicate whether files should be filtered by extension when zipped.
    :type fil_zip: bool
    :ivar fil_cpy: Flag to indicate whether files should be filtered by extension when copied.
    :type fil_cpy: bool
    :ivar fil_mv: Flag to indicate whether files should be filtered by extension when moved.
    :type fil_mv: bool
    :ivar fil_empty: Flag to indicate whether empty zips should be removed after processing.
    :type fil_empty: bool
    :ivar safe: Safety flag to ensure delete operations are performed cautiously.
    :type safe: bool
    :ivar debug: Debugging flag to enable verbose logging.
    :type debug: bool
    """

    src: Path
    dst: Path
    sub_dir: bool
    hash: str
    mv: bool
    cpy: Optional[Path]
    fil_zip: bool
    fil_cpy: bool
    fil_mv: bool
    fil_empty: bool
    safe: bool
    debug: bool
