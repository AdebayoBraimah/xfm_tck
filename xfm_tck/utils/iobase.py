# -*- coding: utf-8 -*-
"""Abstract base class file IO methods, functions and operations.
"""
import os
import subprocess
from warnings import warn

from shutil import (
    copy,
    copytree,
    move
)

from typing import (
    Any,
    List, 
    Tuple,
    Union
)

from abc import (
    ABC,
    abstractmethod
)


class IOBaseObj(ABC):
    """IO abstract base class (``ABC``) object that encapsulates methods related to file and directory manipulation. 

    This ``ABC`` cannot be directly instantiated, and **MUST** used by a child/sub-class that inherits from this class. 
    Additionally, the ``copy`` class method (shown in abstract methods) **MUST** be overwritten when inheriting from this class. 

    Attributes:
        src: Input string that represents a file or directory.
    
    Abstract methods:
        copy: Copies a file or recursively copies a directory using ``copy`` and ``copytree`` from ``shutil``. 
            This method may need to be implemented differently should other aspects of the data need to be preserved (i.e. needing to copy the file metadata with the file).
    
    Usage example:
        >>> # Initialize child class and inherit 
        >>> #   from IOBaseObj ABC
        >>> class SomeFileClass(IOBaseObj):
        ...     def __init__(self, src: str):
        ...         super().__init__(src)
        ...
        ...     # Overwrite IOBaseObj ABC method
        ...     def copy(self, dst: str):
        ...         return super().copy(dst)
        ...         

    Arguments:
        src: Input string that represents a file or directory.
    """
    __slots__ = ( "src" )
    
    def __init__(self,
                 src: str) -> None:
        """Constructor that initializes ``IOBaseObj`` abstract base class."""
        self.src: str = src
        super(IOBaseObj, self).__init__()
    
    def __enter__(self):
        """Context manager entrance method."""
        return self
    
    def __exit__(self, exc_type, exc_val, traceback):
        """Context manager exit method."""
        return False
    
    def __repr__(self):
        """Representation request method."""
        return f"<{self.__class__.__name__} {self.src}>"
    
    def relpath(self, 
                dst: str) -> str:
        """Returns the relative file path to some destination.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC method
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ... 
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.relpath('new_dir/file2.txt'))
            ...
            "../file_namt.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.relpath('new_dir/file2.txt')
            "../file_namt.txt"

        Arguments:
            dst: Destination file path.

        Returns:
            String that reprents the relative file path of the object from the destination file or directory.
        """
        if os.path.isfile(self.src):
            return (os.path.join(
                os.path.relpath(
                    os.path.dirname(self.abspath()),
                    os.path.dirname(dst)),
                    os.path.basename(self.src)))
        else:
            return os.path.relpath(
                self.abspath(),
                os.path.dirname(dst))

    def abspath(self,
                follow_sym_links: bool = False
               ) -> Union[str,None]:
        """Returns the absolute file path.
        
        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC methods
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ...              
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.abspath())
            ...
            "abspath/to/file_namt.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.abspath()
            "abspath/to/file_namt.txt"
        
        Arguments:
            follow_sym_links: If set to true, the absolute path of the symlinked file is returned.
        
        Returns:
            String that represents the absolute file path if it exists, otherwise ``None`` is returned.
        """
        if follow_sym_links and os.path.exists(self.src):
            return os.path.abspath(os.path.realpath(self.src))
        else:
            return os.path.abspath(self.src)
    
    def sym_link(self, 
                 dst: str, 
                 relative: bool = False
                ) -> str:
        """Creates a symbolic link with an absolute or relative file path.

        NOTE: If a directory is the used as the input object, then the linked destination is returned.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC methods
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ...         
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     linked_file: str = file.sym_link("file2.txt")
            ...     print(linked_file)
            ...
            "file2.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.sym_link("file2.txt")
            "file2.txt"

        Arguments:
            dst: Destination file path.
            relative: Symbolically link the file or directory using a relative path.

        Returns:
            String that reprents the absolute path of the sym linked file path.
        """
        src: str = self.abspath(follow_sym_links=True)

        # Create command list
        cmd: List[str] = [ "ln", "-s" ]
        
        if relative and os.path.isdir(dst):
            dst: str = os.path.relpath(dst, src)
        elif relative:
            src: str = self.relpath(dst=dst)
        else:
            src: str = self.abspath(follow_sym_links=True)
        
        if os.path.exists(dst) and os.path.isfile(dst):
            warn(f"WARNING: Symlinked file of the name {dst} already exists. It is being replaced.")
            os.remove(dst)
            cmd.extend([f"{src}",f"{dst}"])
        else:
            cmd.extend([f"{src}",f"{dst}"])
        
        # Execute command
        p: subprocess.Popen = subprocess.Popen(cmd)
        _: Tuple[Any] = p.communicate()
        dst: str = os.path.abspath(dst)
        return dst

    @abstractmethod
    def copy(self, 
             dst: str
            ) -> str:
        """Copies file or recursively copies a directory to some destination.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC methods
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ...         
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     new_file: str = file.copy("file2.txt")
            ...     print(new_file)
            ...
            "/abs/path/to/file2.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.copy("file2.txt")
            "/abs/path/to/file2.txt"

        Arguments:
            dst: Destination file path.

        Return:
            String that corresponds to the copied file or directory.
        """
        src: str = self.abspath(follow_sym_links=True)
        if os.path.isfile(src):
            return os.path.abspath(copy(src=src, dst=dst))
        elif os.path.isdir(src):
            return os.path.abspath(copytree(src=src, dst=dst))
    
    def basename(self) -> str:
        """Retrieves file or directory basename.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC method
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ... 
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.basename())
            ...
            "file_namt.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.basename()
            "file_namt.txt"

        Returns:
            String that represents the basename of the file or directory.
        """
        return os.path.basename(self.src)

    def dirname(self) -> str:
        """Retrieves file or directory basename.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC method
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ... 
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.dirname())
            ...
            "/abs/path/to"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.dirname()
            "/abs/path/to"

        Returns:
            String that represents the directory name of the file or the parent directory of the directory.
        """
        return os.path.dirname(self.abspath())
    
    def move(self, 
             dst: str) -> str:
        """Renames/moves a file/directory. 

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC method
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ... 
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.move("file2.txt"))
            ...
            "file2.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.move("file2.txt")
            "file2.txt"

        Arguments:
            dst: Destination file path.

        Returns:
            String that represents the path of the new file or directory.
        """
        src: str = self.abspath(follow_sym_links=False)
        if os.path.isfile(src):
            return os.path.abspath(move(src=src, dst=dst, copy_function=copy))
        elif os.path.isdir(src):
            return os.path.abspath(move(src=src, dst=dst, copy_function=copytree))
    
    def join(self, *args) -> str:
        """Joins directory or dirname of a file with additional pathname 
        components.

        Usage example:
            >>> # Initialize child class and inherit 
            >>> #   from IOBaseObj ABC
            >>> class SomeFileClass(IOBaseObj):
            ...     def __init__(self, src: str):
            ...         super().__init__(src)
            ...
            ...     # Overwrite IOBaseObj ABC method
            ...     def copy(self, dst: str):
            ...         return super().copy(dst)
            ... 
            >>> # Using class object as context manager
            >>> with SomeFileClass("file_name.txt") as file:
            ...     print(file.join("file2.txt"))
            ...
            "/abs/path/to/dirname/file1/file2.txt"
            >>>
            >>> # OR
            >>> file = SomeFileClass("file_name.txt")
            >>> file.join("file2.txt")
            "/abs/path/to/dirname/file1/file2.txt"

        Arguments:
            *args: Variable length argument list.

        Returns:
            str: New file path with the specified directories.
        """
        src: str = self.abspath(follow_sym_links=False)
        if os.path.isfile(src):
            src: str = os.path.split(src)[0]
            return os.path.join(src, *args)
        elif os.path.isdir(src):
            return os.path.join(src, *args)