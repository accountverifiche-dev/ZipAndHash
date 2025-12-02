import os
import sys
from time import sleep
from pathlib import Path
from typing import Final, Optional


__all__ = ["SingleInstance"]


class SingleInstance:
    """
    Manages a single instance of a process using a file-based lock mechanism.

    This class ensures that only one instance of the process can run at a time
    by creating and locking a specified file. If another process is detected
    to be running with the same lock, it will wait a defined amount of time
    before giving up or exiting. Additionally, it provides context management
    support for automatic acquisition and release of the lock.

    :ivar lockfile: The path to the file used for locking.
    :type lockfile: Path
    :ivar fd: File descriptor for the locked file, used to ensure proper file operations.
    :type fd: int or None
    """
    lockfile: Final[Path]
    fd: Optional[int]

    __MAX_MINUTES_WAITING = 5

    def __init__(self, lockfile: str):
        """
        Initializes the class with the specified lockfile. This constructor sets up
        the necessary parameters for handling the locking mechanism. It takes a
        single argument, `lockfile`, which is used to specify the path to the lock file.

        :param lockfile: The file path representing the lock file to use for locking
                         mechanisms.
        :type lockfile: str
        """
        self.lockfile = Path(lockfile)
        self.fd = None

    def acquire(self):
        """
        Acquire a lock by creating a lockfile and writing the current process ID to it.
        The method continuously tries to create a lockfile using the `os.open` function.
        If the lockfile already exists, it waits and retries until either the lock is
        acquired or the maximum waiting time is exceeded.

        This method ensures that no two processes can acquire the same lockfile at
        the same time. The lockfile contains the process ID of the current process
        that holds the lock.

        :raises FileExistsError: If the lockfile already exists and cannot be
                                 acquired within the maximum time allowed.
        :raises SystemExit: If the maximum waiting time is exceeded without
                            acquiring the lock.
        """
        i = 0
        while i >= 0:
            try:
                self.fd = os.open(
                    self.lockfile,
                    os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                os.write(self.fd, str(os.getpid()).encode())
                i = -1
            except FileExistsError:
                if i == 0:  # pragma: no cover
                    print(f"Process already executing (lock: {self.lockfile}), waiting...", file=sys.stderr)
                if i >= self.__MAX_MINUTES_WAITING * 60 * 10:
                    print(f"Maximum wait exceeded ({self.__MAX_MINUTES_WAITING} minutes), giving up.", file=sys.stderr)
                    sys.exit(1)
                sleep(0.1)
                i += 1

    def release(self):
        """
        Releases the lock by closing the file descriptor and deleting the lock file.

        This method is responsible for properly releasing the acquired lock by closing
        the associated file descriptor and removing the lock file from the file system.
        It ensures that resources are appropriately cleaned up after use.

        :return: None
        """
        if self.fd:
            os.close(self.fd)
            self.fd = None
            self.lockfile.unlink(missing_ok=True)

    def __enter__(self):
        """
        Context manager entry method for acquiring the resource.

        This method is called when the object is used as a context manager
        in a 'with' statement. It acquires the necessary resource for usage
        within the context and then allows access to the object.

        :return: The context manager instance after the resource is acquired.
        :rtype: object
        """
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Handle cleanup and resource release when exiting a context.

        This method is a standard part of the context management protocol
        and is automatically invoked when using an object in a 'with' statement.
        The method ensures that resources are properly released upon exiting the context.

        :param exc_type: Exception type if an exception occurred, otherwise None.
        :type exc_type: Type[BaseException] | None
        :param exc_value: The exception instance if an exception occurred, otherwise None.
        :type exc_value: BaseException | None
        :param tb: Traceback object if an exception occurred, otherwise None.
        :type tb: TracebackType | None
        :return: Always returns None to suppress exception propagation explicitly.
        :rtype: None
        """
        self.release()
