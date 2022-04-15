# -*- coding: utf-8 -*-
"""File IO methods, functions and operations.
"""
import os
import nibabel as nib
from warnings import warn

from typing import Optional, Tuple

from xfm_tck.utils.iobase import IOBaseObj
from xfm_tck.utils.enums import NiiHeaderField


class InvalidNiftiFileError(Exception):
    """Exception intended for invalid NIFTI files."""

    pass


class File(IOBaseObj):
    """File object base class that inherits from the ``IOBaseObj`` abstract base class. 
    This class creates a ``File`` object that encapsulates a number of methods and properites for file and filename handling, and file manipulation.
    
    Attributes:
        src: Input file.
        ext: File extension of input file. If no extension is provided, it is inferred.

    Usage example:
        >>> # Using class object as context manager
        >>> with File("file_name.txt") as file:
        ...     file.touch()
        ...     file.write_txt("some text")
        ...
        >>> # or
        >>> 
        >>> file = File("file_name.txt")
        >>> file
        "file_name.txt"

    Arguments:
        src: Input file (need not exist at runtime/instantiated).
        ext: File extension of input file. If no extension is provided, it is inferred.
        assert_exists: Asserts that the specified input file must exist. 
    """

    __slots__ = ("src", "ext")

    def __init__(
        self, src: str, ext: Optional[str] = "", assert_exists: bool = False
    ) -> None:
        """Initialization method for the File base class.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     file.touch()
            ...     file.write_txt("some text")
            ...     print(file.src)
            ...
            "file_name.txt"
            >>>
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file
            "file_name.txt"

        Arguments:
            src: Input file (need not exist at runtime/instantiated).
            ext: File extension of input file. If no extension is provided, it is inferred.
            assert_exists: Asserts that the specified input file must exist. 
        """
        self.src: str = src
        if ext:
            self.ext: str = ext
        else:
            self.ext: str = None
        super(File, self).__init__(src)

        if ext:
            self.ext: str = ext
        elif self.src.endswith(".gz"):
            self.ext: str = self.src[-7:]
        else:
            _, self.ext = os.path.splitext(self.src)

        if assert_exists:
            assert os.path.exists(self.src), f"Input file {self.src} does not exist."

    def copy(self, dst: str) -> str:
        """Copies file to some source destination.

        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     new_file: str = file.copy("file2.txt")
            ...
            >>> new_file
            "/abs/path/to/file2.txt"
            >>>
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.copy("file2.txt")
            "/abs/path/to/file2.txt"

        Arguments:
            dst: Destination file path.
            relative: Symbolically link the file using a relative path.

        Returns:
            String that corresponds to the copied file.
        """
        return super().copy(dst)

    def touch(self) -> None:
        """Creates an empty file.

        This class mehtod is analagous to UNIX's ``touch`` command.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     file.touch()
            ...
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.touch()
        """
        if os.path.exists(self.src):
            print(f"The file: {self.src} already exists.")
        else:
            with open(self.src, "w") as _:
                pass
        return None

    def rm_ext(self, ext: str = "") -> str:
        """Removes file extension from the file.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     file.touch()
            ...     print(file.rm_ext())
            ...
            "file_name"
            >>> 
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.rm_ext()
            "file_name"
        
        Arguments:
            ext: File extension.
        
        Returns:
            Filename as string with no extension.
        """
        if ext:
            ext_len: int = len(ext)
            return self.src[:-(ext_len)]
        elif self.ext:
            ext_len = len(self.ext)
            return self.src[:-(ext_len)]
        else:
            return self.src[:-(4)]

    def write(self, txt: str = "") -> None:
        """Writes/appends text to file.

        NOTE:
            Text written to file is ALWAYS utf-8 encoded.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     file.write("<Text to be written>")
            ...
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.write("<Text to be written>")
        
        Arguments:
            txt: Text/string to be written to file.
        """
        with open(self.src, mode="a", encoding="utf-8") as tmp_file:
            tmp_file.write(txt)
            tmp_file.close()
        return None

    def file_parts(self, ext: str = "") -> Tuple[str, str, str]:
        """Similar to MATLAB's ``fileparts``, this function splits a file and its path into its constituent parts:

            * file path
            * filename
            * extension
        
        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     print(file.file_parts())
            ...
            ("path/to/file", "filename", ".txt")
            >>> 
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.file_parts()
            ("path/to/file", "filename", ".txt")
        
        Arguments:
            ext: File extension, needed if the file extension of file object is longer than 4 characters.
        
        Returns:
            Tuple: 
                * Absolute file path, excluding filename.
                * Filename, excluding extension.
                * File extension.
        """
        file: str = self.src
        file: str = os.path.abspath(file)

        path, _filename = os.path.split(file)

        if ext:
            ext_num: int = len(ext)
            _filename: str = _filename[:-(ext_num)]
            [filename, _] = os.path.splitext(_filename)
        elif self.ext:
            ext: str = self.ext
            ext_num: int = len(ext)
            _filename: str = _filename[:-(ext_num)]
            [filename, _] = os.path.splitext(_filename)
        else:
            [filename, ext] = os.path.splitext(_filename)

        return (path, filename, ext)

    def remove(self) -> None:
        """Removes file.

        Usage example:
            >>> # Using class object as context manager
            >>> with File("file_name.txt") as file:
            ...     file.remove()
            ...
            >>> 
            >>> # or
            >>> 
            >>> file = File("file_name.txt")
            >>> file.remove()
        """
        return os.remove(self.abspath())


class NiiFile(File):
    """NIFTI file class specific for NIFTI files which inherits class methods from the ``File`` base class.

    Attributes:
        src: Input NIFTI file path.
        ext: File extension of input file.
    
    Usage example:
        >>> # Using class object as context manager
        >>> with NiiFile("file.nii") as nii:
        ...     print(nii.file_parts())
        ...
        ("path/to/file", "file", ".nii")
        >>> 
        >>> # or
        >>> 
        >>> nii = NiiFile("file.nii")
        >>> nii
        "file.nii"
        >>> nii.abspath()
        "abspath/to/file.nii"
        >>> 
        >>> nii.rm_ext()
        "file"
        >>>
        >>> nii.file_parts()
        ("path/to/file", "file", ".nii")
    
    Arguments:
        src: Path to NIFTI file.
        
    Raises:
        InvalidNiftiFileError: Exception that is raised in the case **IF** the specified NIFTI file exists, but is an invalid NIFTI file.
    """

    def __init__(
        self, src: str, assert_exists: bool = False, validate_nifti: bool = False
    ) -> None:
        """Initialization method for the NiiFile class.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with NiiFile("file.nii") as nii:
            ...     print(nii.abspath())
            ...     print(nii.src)
            ...     print(nii.file_parts())
            ...
            "abspath/to/file.nii"
            "file"
            ("path/to/file", "file", ".nii")
            >>> 
            >>> # or
            >>> 
            >>> nii = NiiFile("file.nii")
            >>> nii
            "file.nii"
            >>> nii.abspath()
            "abspath/to/file.nii"
            >>> 
            >>> nii.rm_ext()
            "file"
            >>>
            >>> nii.file_parts()
            ("path/to/file", "file", ".nii")
        
        Arguments:
            file: Path to NIFTI file.
            assert_exists: Asserts that the specified input file must exist. 
            validate_nifti: Validates the input NIFTI file if it exists.
        
        Raises:
            InvalidNiftiFileError: Exception that is raised in the case **IF** the specified NIFTI file exists, but is an invalid NIFTI file.
        """
        self.src: str = src
        super(NiiFile, self).__init__(src)

        if self.src.endswith(".nii.gz"):
            self.ext: str = ".nii.gz"
        elif self.src.endswith(".nii"):
            self.ext: str = ".nii"
        else:
            self.ext: str = ".nii.gz"
            self.src: str = self.src + self.ext

        if assert_exists:
            assert os.path.exists(
                self.src
            ), f"Input NIFTI file {self.src} does not exist."

        if validate_nifti and os.path.exists(self.src):
            try:
                _: nib.Nifti1Image = nib.load(filename=self.src)
            except Exception as error:
                raise InvalidNiftiFileError(
                    f"The NIFTI file {self.src} is not a valid NIFTI file and raised the following error {error}."
                )

    # Overwrite several File base class methods
    def touch(self) -> None:
        """This class method is not implemented and will simply return None, and is not relevant/needed for NIFTI files.
        """
        return None

    def write(self, txt: str = "", header_field: str = "intent_name") -> None:
        """This class method writes relevant information to the NIFTI file header.
        This is done by writing text to either the ``descrip`` or ``intent_name``
        field of the NIFTI header.

        NOTE:
            * The ``descrip`` NIFTI header field has limitation of 24 bytes - meaning that only a string of 24 characters can be written without truncation.
            * The ``intent_name`` NIFTI header field has limitation of 16 bytes - meaning that only a string of 16 characters can be written without truncation.
        
        Usage example:
            >>> # Using class object as context manager
            >>> with NiiFile("file.nii") as nii:
            ...     nii.write(txt='Source NIFTI',
            ...               header_field='intent_name')
            ...
            >>> # or
            >>> 
            >>> nii = NiiFile("file.nii")
            >>> nii.write(txt='Source NIFTI',
            ...           header_field='intent_name')

        Arguments:
            txt: Input text to be added to the NIFTI file header.
            header_field: Header field to have text added to.
        """
        img: nib.Nifti1Image = nib.load(self.src)
        header_field: str = NiiHeaderField(header_field).name

        if header_field == "descrip":
            if len(txt) >= 24:
                warn(
                    f"WARNING: The input string is longer than the allowed limit of 24 bytes/characters for the '{header_field}' header field."
                )
            img.header["descrip"] = txt
        elif header_field == "intent_name":
            if len(txt) >= 16:
                warn(
                    f"WARNING: The input string is longer than the allowed limit of 16 bytes/characters for the '{header_field}' header field."
                )
            img.header["intent_name"] = txt
        return None
