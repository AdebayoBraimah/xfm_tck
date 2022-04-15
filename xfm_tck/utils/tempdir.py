# -*- coding: utf-8 -*-
"""Temporary working directory and file module.
"""
import os
import random

from typing import Optional

from xfm_tck.utils.workdir import WorkDir
from xfm_tck.utils.fileio import File


class TmpDir(WorkDir):
    """Temporary directory class that creates (random) temporary directories and files given a parent directory. 
    This class inherits methods from the ``WorkDir`` base class.
    
    Attributes:
        src: Input temproary working directory.
        parent_dir: Parent directory of the specified temproary directory.
    
    Usage example:
            >>> with TmpDir("/path/to/temporary_directory",False) as tmp_dir:
            ...     tmp_dir.mkdir()
            ...     # do more stuff
            ...     tmp_dir.rmdir(rm_parent=False)
            ...
            >>> # or
            >>>
            >>> tmp_dir = TmpDir("/path/to/temporary_directory")
            >>> tmp_dir
            "/path/to/temporary_directory"
            >>> tmp_dir.rmdir(rm_parent=False)
        
    Arguments:
        src: Temporary parent directory name/path.
        use_cwd: Use current working directory as working direcory.
    """

    def __init__(self, src: str, use_cwd: bool = False) -> None:
        """Initialization method for the TmpDir child class.
        
        Usage example:
            >>> with TmpDir("/path/to/temporary_directory",False) as tmp_dir:
            ...     tmp_dir.mkdir()
            ...     # do more stuff
            ...     tmp_dir.rmdir(rm_parent=False)
            ...
            >>> # or
            >>> tmp_dir = TmpDir("/path/to/temporary_directory")
            >>> tmp_dir
            "/path/to/temporary_directory"
            >>> tmp_dir.rmdir(rm_parent=False)
        
        Arguments:
            src: Temporary parent directory name/path.
            use_cwd: Use current working directory as working direcory.
        """
        _n: int = 10000
        self.src: str = os.path.join(src, "tmp_dir_" + str(random.randint(0, _n)))

        if use_cwd:
            _cwd: str = os.getcwd()
            self.src = os.path.join(_cwd, self.src)
        super(TmpDir, self).__init__(self.src, use_cwd)

    def __exit__(self, exc_type, exc_val, traceback):
        """Context manager exit method for ``TmpDir`` class."""
        self.rmdir()
        return super().__exit__(exc_type, exc_val, traceback)

    class TmpFile(File):
        """Sub-class of ``TmpDir`` class, which creates and manipulates temporary files via inheritance from the ``File`` object base class.
        
        Attributes:
            file: Temporary file name.
            ext: File extension of input file. If no extension is provided, it is inferred.
        
        Usage example:
            >>> tmp_directory = TmpDir("/path/to/temporary_directory")
            >>>
            >>> temp_file = TmpDir.TmpFile(tmp_directory.tmp_dir,
            ...                             ext="txt")
            ...
            >>> temp_file
            "/path/to/temporary_directory/temporary_file.txt"
        
        Arguments:
            tmp_dir: Temporary directory name.
            tmp_file: Temporary file name.
            ext: Temporary directory file extension.
        """

        def __init__(
            self, tmp_dir: str, tmp_file: Optional[str] = "", ext: Optional[str] = "",
        ) -> None:
            """Initialization method for the TmpFile sub-class that inherits from the ``File`` base class, allowing for the creation and maninuplation of temporary files.
            
            Usage example:
                >>> tmp_directory = TmpDir("/path/to/temporary_directory")
                >>>
                >>> temp_file = TmpDir.TmpFile(tmp_directory.tmp_dir,
                ...                             ext=".txt")
                ...
                >>> temp_file
                "/path/to/temporary_directory/temporary_file.txt"
            
            Arguments:
                tmp_dir: Temporary directory name.
                tmp_file: Temporary file name.
                ext: File extension.
            """
            if tmp_file:
                pass
            else:
                _n: int = 10000
                tmp_file: str = "tmp_file_" + str(random.randint(0, _n))

            if ext:
                if "." in ext:
                    pass
                else:
                    ext: str = f".{ext}"
                tmp_file: str = tmp_file + f"{ext}"

            tmp_file: str = os.path.join(tmp_dir, tmp_file)
            super(TmpDir.TmpFile, self).__init__(tmp_file, ext)
