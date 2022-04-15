# -*- coding: utf-8 -*-
"""Working directory module.
"""
import os
import shutil

from xfm_tck.utils.iobase import IOBaseObj


class WorkDir(IOBaseObj):
    """Working directory base class that instantiates ``WorkDir`` objects that creates and manipulates working directories.

    Attributes:
        src: Input working directory.
        parent_dir: Parent directory.

    Usage example:
            >>> # Using class object as context manager
            >>> ## Create work directory , then clean-up (remove it)
            >>> with WorkDir(src="/path/to/working_directory", use_cwd=False) as work:
            ...     work.mkdir()
            ...     work.rmdir(rm_parent=False)
            ...
            >>> # or
            >>>
            >>> work = WorkDir(src="/path/to/working_directory", 
            ...                use_cwd=False)
            >>> work.mkdir()
            >>> work
            "/path/to/working_directory"
            >>> work.rmdir(rm_parent=False)

    Arguments:
        src: Working directory name/path. This directory need not exist at runtime.
        use_cwd: Use current working directory as the parent directory.
    """

    __slots__ = ("src", "parent_dir")

    def __init__(self, src: str, use_cwd: bool = False) -> None:
        """Initialization method for the ``WorkDir`` base class.

        Usage example:
            >>> # Using class object as context manager
            >>> ## Create work directory , then clean-up (remove it)
            >>> with WorkDir(src="/path/to/working_directory", use_cwd=False) as work:
            ...     work.mkdir()
            ...     work.rmdir(rm_parent=False)
            ...
            >>> # or
            >>>
            >>> work = WorkDir(src="/path/to/working_directory", 
            ...                use_cwd=False)
            >>> work.mkdir()
            >>> work
            "/path/to/working_directory"
            >>> work.rmdir(rm_parent=False)
        
        Arguments:
            src: Working directory name/path. This directory need not exist at runtime.
            use_cwd: Use current working directory as the parent directory.
        """
        self.src: str = src
        self.parent_dir: str = os.path.dirname(self.src)
        super(WorkDir, self).__init__(src)

        if use_cwd:
            _cwd: str = os.getcwd()
            self.src: str = os.path.join(_cwd, self.src)
            self.parent_dir: str = os.path.dirname(self.src)

    def __enter__(self):
        """Context manager entrance method for ``WorkDir`` class."""
        if not self.exists():
            self.mkdir()
        return super().__enter__()

    def mkdir(self) -> None:
        """Makes/creates the working directory.

        This class method is analogous to UNIX's ``mkdir -p`` command and option combination.

        Usage example:
            >>> # Using class object as context manager
            >>> with WorkDir(src="/path/to/working_directory", use_cwd=False) as work:
            ...     work.mkdir()
            ...
            >>> # or
            >>>
            >>> work = WorkDir(src="/path/to/working_directory", 
            ...                use_cwd=False)
            >>> work.mkdir()
            >>> work
            "/path/to/working_directory"
        """
        if not self.exists():
            return os.makedirs(self.src)
        else:
            return None

    def rmdir(self, rm_parent: bool = False) -> None:
        """Removes working directory, and the parent directory if indicated to do so.

        This class method is analogous to UNIX's ``rm -rf`` command and option combination.

        Usage example:
            >>> # Using class object as context manager
            >>> with WorkDir(src="/path/to/working_directory", use_cwd=False) as work:
            ...     work.mkdir()
            ...     work.rmdir(rm_parent=False)
            ...
            >>> # or
            >>>
            >>> work = WorkDir(src="/path/to/working_directory", 
            ...                use_cwd=False)
            >>> work.mkdir()
            >>> work.rmdir(rm_parent=False)

        Arguments:
            rm_parent: Removes parent directory as well.
        """
        if rm_parent and os.path.exists(self.parent_dir):
            return shutil.rmtree(self.parent_dir, ignore_errors=True)
        elif os.path.exists(self.src):
            return shutil.rmtree(self.src, ignore_errors=True)
        else:
            return None

    def copy(self, dst: str) -> str:
        """Recursively copies a directory to some destination.

        Usage example:
            >>> # Using class object as context manager
            >>> with WorkDir("/path/to/working_directory") as work_dir:
            ...     work: str = work_dir.copy("/path/to/new/directory")
            ...
            >>> work
            "/path/to/new/directory"
            >>>
            >>> # or
            >>> 
            >>> work = WorkDir("/path/to/working_directory")
            >>> work.copy("/path/to/new/directory")
            "/path/to/new/directory"

        Arguments:
            dst: Destination file path.

        Returns:
            String that corresponds to the copied work.
        """
        return super().copy(dst)

    def exists(self) -> bool:
        """Tests if a directory exists.

        Usage example:
            >>> # Using class object as context manager
            >>> with WorkDir("/path/to/working_directory") as work_dir:
            ...     print(work_dir.exists())
            ...
            False
            >>>
            >>> # or
            >>> 
            >>> work = WorkDir("/path/to/working_directory")
            >>> work.exists()
            False

        Returns:
            Returns ``True`` if the directory exists and ``False`` otherwise.
        """
        src: str = self.abspath()
        if os.path.isdir(src) and os.path.exists(src):
            return True
        else:
            return False
