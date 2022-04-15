# -*- coding: utf-8 -*-
"""Utility module for ``xfm_tck`` tractography pipeline.
"""
import os
import json

from time import time
from json import JSONDecodeError

from typing import (
    Any,
    Dict,
    Optional,
)

from xfm_tck.utils.fileio import File
from xfm_tck.utils.logutil import LogFile
from xfm_tck.utils.tempdir import TmpDir


# Globlally define (temporary) log file object
with TmpDir(src=os.getcwd()) as tmpd:
    with TmpDir.TmpFile(tmp_dir=tmpd.src, ext='.log') as tmpf:
        log: LogFile = LogFile(log_file=tmpf.src)


def timeops(log: Optional[LogFile] = None) -> callable:
    """Decorator function that times some operation and writes that time to
    a log file object.

    Usage example:
        >>> from fmri_preproc.utils.logutil import LogFile
        >>> log = LogFile('my_log_file.log')
        >>>
        >>> @timeops(log)
        >>> def my_func(args*, log):
        ...     for i in args:
        ...         log.log(f"This is an arg: {i}")
        ...     return None
        ...
        >>> # The length of time to complete the operation 
        >>> # should be written to the log file.
        >>> myfunc(args*, log)  

    Arguments:
        log: Log file object to be written to.
    """
    def decor(func: callable) -> callable:
        """Inner decorated function that accepts functions."""
        def timed(*args,**kwargs) -> callable:
            """Nested decorator function the performs timing of an operation.
            """
            start: float = time()
            if log: log.log(f"BEGIN: {func.__name__}", use_header=True)
            result: callable = func(*args,**kwargs)
            end: float = time()
            if log: log.log(f"END: {func.__name__}  |  Time elapsed: {(end - start):2f} sec.", use_header=True)
            return result
        return timed
    return decor


def json2dict(jsonfile: str) -> Dict[Any,Any]:
    """Read JSON file to dictionary.
    """
    d: Dict = {}
    with open(jsonfile, 'r') as file:
        try:
            d: Dict[Any,Any] = json.load(file)
        except JSONDecodeError:
            pass
    return d


def dict2json(dict: Dict[Any,Any],
              jsonfile: str,
              indent: int = 4
             ) -> str:
    """Write dictionary to JSON file.
    """
    with open(jsonfile, 'w') as out:
        json.dump(dict, out, indent=indent)
    return jsonfile


def update_sidecar(file: str, **kwargs) -> str:
    """Updates a JSON sidecar/file.
    """
    with File(src=file, assert_exists=False) as f:
        dirname, basename, _ = f.file_parts()
        jsonfile: str = os.path.join(dirname,basename + '.json')
        with File(src=jsonfile) as jf:
            jsonfile: str = jf.abspath()
    
    d: Dict[Any,Any] = load_sidecar(file=jsonfile)
    d.update(**kwargs)
    jsonfile: str = dict2json(dict=d, jsonfile=jsonfile, indent=4)

    return jsonfile


def load_sidecar(file: str) -> Dict[Any,Any]:
    """Reads in a JSON sidecar/file.
    """
    d: Dict[Any,Any] = {}
    with File(src=file, assert_exists=False) as f:
        dirname, basename, _ = f.file_parts()
        jsonfile: str = os.path.join(dirname,basename + '.json')
        with File(src=jsonfile) as jf:
            if os.path.exists(jf.abspath()):
                with open(jf.abspath(),'r') as j:
                    d.update(json.load(j))
    return d


def get_fsl_version() -> str:
    """Returns a string that represents the version of ``FSL`` in the system path.
    """
    fsl_version_file: str = os.path.join(os.environ['FSLDIR'], 'etc/fslversion')
    with open(fsl_version_file, 'r') as file:
        ver: str = file.read().split(':')[0]
    return ver