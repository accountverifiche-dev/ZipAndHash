import sys
import logging
import argparse
import shutil
from pathlib import Path
from typing import List, Optional, Dict

from zah.config import *
from zah.single_instance import *
from zah.dir_operations import *
from zah.zip import *
from zah.hash import *
from zah.logger import *
from zah.extensions import *

script_name = "zipandhash"
config: Config
log: Optional[logging.Logger] = None


__all__ = ["main"]


def init(argv: List[str]) -> None:
    """
    Initializes the configuration and logging for the program based on the command-line
    arguments provided by the user.

    Parses the command-line arguments to configure the behavior of the application,
    such as specifying the source and destination directories, enabling or disabling
    various flags, selecting a hash algorithm, and toggling debug mode. Sets up the
    logging functionality for the application with an optional debug mode.

    :param argv: Command-line arguments passed to the application
    :type argv: List[str]
    :return: None
    """
    global config, log
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str, help="Path to source directory")
    parser.add_argument("dst", type=str, help="Path to destination directory")
    parser.add_argument("--sub", action="store_true", help="Create a subdirectory in dst", default=False)
    parser.add_argument("--hash", type=str, help="Hash algorithm", choices=algorithms, default="sha3_256")
    parser.add_argument("--mv", action="store_true", help="Delete source files at the end of the process")
    parser.add_argument("--cpy", type=str, default="", help="Make a copy in the given directory")
    parser.add_argument("--fzip", action="store_true", help="Filter files in zip", default=False)
    parser.add_argument("--fcpy", action="store_true", help="Filter files in cpy", default=False)
    parser.add_argument("--fmv", action="store_true", help="Filter files in mv", default=False)
    parser.add_argument("--fmpt", action="store_true", help="Filter empty zips", default=False)
    parser.add_argument("--unsafe", action="store_true", help="Disable safety checks", default=False)
    parser.add_argument("--debug", action="store_true", help="Enable debug mode", default=False)

    args, _unknown = parser.parse_known_args(argv)
    setup_logging(args.debug, f"{script_name}.log")
    log = logging.getLogger(script_name)
    log.debug(f"Args: {args.__dict__}" + (f"Unknown args: {_unknown}" if _unknown else ""))

    config = Config(
        src=Path(args.src),
        dst=Path(args.dst),
        sub_dir=args.sub,
        hash=args.hash,
        mv=args.mv,
        cpy=Path(args.cpy) if args.cpy else None,
        fil_zip=args.fzip,
        fil_cpy=args.fcpy,
        fil_mv=args.fmv,
        fil_empty=args.fmpt,
        safe= not args.unsafe,
        debug=args.debug,
    )


def run() -> None:
    """
    Run the main process to zip directories, calculate hashes, optionally copy or move files.

    The function handles several steps:
    1. Checks the validity of a source (`src`) and a destination (`dst`) directories.
    2. Zips all subdirectories in the source directory and stores the resulting zip files
       in the destination directory. Depending on configuration, it filters files during
       the zipping process or includes all files.
    3. Calculates hashes for each zip file using the specified hash algorithm and stores
       these hashes in a text file. It also calculates the hash of this text file.
    4. If requested, copies the source and destination directories into a separate
       directory while optionally filtering files during the copy process.
    5. If requested, moves the source directory into the destination directory.
       This step includes an optional safety confirmation before clearing the source directory.

    During the process, informative messages are logged, detailing the operations performed.
    Errors are raised for invalid directories or user-confirmation failures, ensuring safety
    in file operations.

    :raises NotADirectoryError:
        Raised if an expected directory is invalid during operations, such as the destination
        or copy directories.

    :raises RuntimeError:
        Raised if the user fails to confirm an operation during the safety confirmation step.

    :return: None
    """
    # -----------------------------------------------------------------------------------------------------------------
    # ZIP ALL THE DIRECTORIES IN THE SRC DIRECTORY, INTO THOSE MANY FILES INSIDE THE DST DIRECTORY
    # -----------------------------------------------------------------------------------------------------------------
    check_paths(config.src, config.dst, config.cpy)
    log.debug(f"Paths checked successfully")

    log.info(f"Starting zip process for directory {config.src}...")
    sub_dir: Optional[str] = None
    if config.sub_dir:
        sub_dir = input("Insert subdirectory name: ")
        dst_dir = config.dst / sub_dir
        dst_dir.mkdir(parents=True, exist_ok=True)
        if not dst_dir.is_dir():
            raise NotADirectoryError(f"Destination directory {dst_dir} is not a directory") # pragma: no cover
    else:
        dst_dir = config.dst
    log.info(f"...into destination directory {dst_dir} with{"out" if config.fil_zip else ""} filter")

    zip_files: List[Path] = []
    for src_dir in get_subdirectories(config.src):
        dst_zip, files_in_zip = zip_directory(src_dir, dst_dir, allowed_ext if config.fil_zip else None, config.fil_empty)
        if dst_zip:
            zip_files.append(dst_zip)
            log.debug(f"Zip file {dst_zip} created successfully ({files_in_zip} files)")
        else:
            log.info(f"Directory {src_dir} not zipped (empty directory or no files allowed by filter)")
    log.info(f"Zip process completed successfully ({len(zip_files)} directories zipped)")

    # -----------------------------------------------------------------------------------------------------------------
    # CALCULATE THE HASH OF EACH ZIP FILE AND SAVE THEM IN A TXT FILE, THEN CALCULATE THE HASH OF THE TXT
    # -----------------------------------------------------------------------------------------------------------------
    hashes: Dict[str, str] = {}
    for zip_file in zip_files:
        h = hash_file(zip_file, config.hash)
        hashes[zip_file.name] = h
        log.debug(f"Hash ({config.hash}) of {zip_file.name}: {h}")

    hashes_file = dst_dir / "hashes.txt"
    with hashes_file.open("w") as f:
        f.writelines([f"{k} ({config.hash}): {v}\n" for k, v in hashes.items()])
    log.info(f"Hash process completed successfully ({len(hashes)} files hashed)")

    h = hash_file(hashes_file, config.hash)
    log.critical(f"Final hash ({config.hash}): {h}")

    # -----------------------------------------------------------------------------------------------------------------
    # COPY EVERYTHING IN THE CPY DIRECTORY, IF REQUESTED
    # -----------------------------------------------------------------------------------------------------------------
    if config.cpy:
        if sub_dir:
            cpy_dir = config.cpy / sub_dir
            cpy_dir.mkdir(parents=True, exist_ok=True)
            if not cpy_dir.is_dir():
                raise NotADirectoryError(f"Copy directory {cpy_dir} is not a directory") # pragma: no cover
        else:
            cpy_dir = config.cpy
        log.debug(f"Copying src and dst into {cpy_dir} with{"out" if config.fil_cpy else ""} filter")

        shutil.copytree(dst_dir, cpy_dir, dirs_exist_ok=True)
        if config.fil_cpy:
            copy_filtered(config.src, cpy_dir, allowed_ext)
        else:
            shutil.copytree(config.src, cpy_dir, dirs_exist_ok=True)

        log.info(f"Copy process completed successfully into directory {cpy_dir}")

    # -----------------------------------------------------------------------------------------------------------------
    # MOVE SRC IN THE DST DIRECTORY, IF REQUESTED, ASKING CONFIRM
    # -----------------------------------------------------------------------------------------------------------------
    if config.mv:
        log.debug(f"Moving src into {dst_dir} with{"out" if config.fil_mv else ""} filter")
        if config.fil_mv:
            copy_filtered(config.src, dst_dir, allowed_ext)
        else:
            shutil.copytree(config.src, dst_dir, dirs_exist_ok=True)
        log.debug(f"Copied src into {dst_dir}")
        if config.safe:
            confirm = input(f"Check if {dst_dir} contains the src files and write Y to confirm: ").upper()
            if confirm != "Y":
                raise RuntimeError("User did not confirm the copy: aborting process...")
        for src_dir in get_subdirectories(config.src):
            clear_folder(src_dir)
            log.debug(f"Cleared directory {src_dir}")
        log.info(f"Move process completed successfully into directory {dst_dir}")
    log.info("Process completed successfully")
    input(f"Press ENTER to exit...")


def main() -> None:
    """
    Main function that initializes and runs the application. It uses a lock to
    ensure a single instance of the script is running at any given time.
    Handles initialization, logging, and error management throughout
    execution.

    :raises Exception: If an unexpected error occurs during initialization
        or execution of the application.

    :return: None
    """
    with SingleInstance(f"{script_name}.lock"):
        try:
            init(sys.argv[1:])
            run()
        except Exception as e:
            if log:
                log.error(f"{e}")
            else:
                raise e
