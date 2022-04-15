# -*- coding: utf-8 -*-
"""Command module for UNIX command line interactions.
"""
import os
import subprocess
import shlex
import shutil

from dataclasses import dataclass

from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)

from xfm_tck.utils.fileio import File
from xfm_tck.utils.logutil import LogFile


class DependencyError(Exception):
    """Exception intended for unment dependencies"""
    pass


@dataclass
class Command:
    """Creates a command object for UNIX command line binaries/programs/applications to be executed. Primary use and 
    use-cases are intended for the subprocess module and its associated classes (i.e. Popen/call/run).

    The input argument is a command (string).

    NOTE: 
        The specified command used must be in system path.
    
    Attributes:
        command: Command to be executed/run on the command line.
        env: Dictionary of environment variables to add to subshell.
    
    Usage example:
        >>> echo = Command("echo 'Hi! I have arrived!'")
        >>> echo
        Command(command="echo 'Hi! I have arrived!'", env=None)
        >>>
        >>> echo.run()
        (0, None, None)
        Hi! I have arrived! # Output is directed to the shell
    
    Arguments:
        command: Command to be used.
        env: Dictionary of environment variables to add to subshell.
    """
    command: str
    env: Dict[str,str] = None
    
    def check_dependency(self) -> bool:
        """Checks the dependency of some command line executable. Should the 
        dependency not be met, then an exception is raised. Check the 
        system path should problems arise and ensure that the executable
        of interest is installed and is in the system path.
        
        Usage example:
            >>> figlet = Command("figlet python")
            >>> figlet.check_dependency()   # Raises exception if not in system path

        Returns:
            Returns True if dependency is met, raises exception otherwise.
        
        Raises:
            DependencyError: Dependency error exception is raised if the dependency is not met.
        """
        _tmp: List[str] = shlex.split(self.command)
        _cmd: str = _tmp[0]

        if not shutil.which(_cmd):
            raise DependencyError(f"Command executable not found in system path: {_cmd}")
        return True
    
    def run(self,
            log: Optional[Union[LogFile,str]] = None,
            debug: bool = False,
            dryrun: bool = False,
            stdout: str = None,
            shell: bool = False,
            raise_exc: bool = True
           ) -> Tuple[int,Union[str,None],Union[str,None]]:
        """Uses python's built-in ``subprocess`` module to execute (run) a command from a command.
        The standard output and error can optionally be written to file.
        
        NOTE: 
            * The contents of the ``stdout`` output file will be empty if ``shell`` is set to ``True``.
        
        Usage example:
            >>> echo = Command("echo 'Hi! I have arrived!'")
            >>> echo
            Command(command="echo 'Hi! I have arrived!'", env=None)
            >>>
            >>> # Run/execute command
            >>> echo.run()
            (0, '', '')
        
        Arguments:
            log: ``LogFile`` object or ``str``.
            debug: Sets logging function verbosity to DEBUG level.
            dryrun: Dry run -- does not run task. Command is recorded to the log file.
            stdout: Output file to write standard output to.
            shell: Use shell to execute command.
            raise_exec: If true, raises ``RuntimeError`` exception if the return code of the command is not 0 - otherwise no exception is raised with non-0 return codes.
            
        Returns:
            * Return code for command execution (``int``).
            * Standard output writtent to file should the 'stdout' option be used (``str``).
            * Standard error writtent to file should the 'stdout' option be used (``str``).
        
        Raises:
            RuntimeError: Exception that is raised if the return code of the command is not 0 and the ``raise_exc`` argument is set to ``True``.
        """
        cmd: List[str] = shlex.split(s=self.command, comments=False, posix=True)

        if type(log) is str:
            log: LogFile = LogFile(log_file=log)

        if log and debug:
            log.debug(f"Running:\t{self.command}")
        elif log:
            log.info(f"Running:\t{self.command}")
        
        if log and dryrun:
            log.info(f"Performing command as a dry run.")
            return 0, None, None
        
        # Define environment and environmental variables
        merged_env: Dict[str,str] = os.environ
        if self.env is not None:
            merged_env.update(self.env)

        p: subprocess.Popen = subprocess.Popen(cmd,
                                               shell=shell,
                                               env=merged_env,
                                               stdout=subprocess.PIPE,
                                               stderr=subprocess.PIPE)
        
        # Write output files
        out,err = p.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')

        # Standard output/error files
        if stdout is not None:
            stderr: str = os.path.splitext(str(stdout))[0] + ".err"

            with File(src=stdout) as stout:
                with File(src=stderr) as sterr:
                    stout.write(out)
                    sterr.write(err)
                    stdout: str = stout.abspath()
                    stderr: str = sterr.abspath()
        else:
            stdout: str = None
            stderr: str = None

        if p.returncode != 0:
            if log: log.error(f"Failed:\t{self.command} with return code {p.returncode}")
            if raise_exc: raise RuntimeError(f"\nFailed:\t{self.command} with return code {p.returncode}\n")

        return (p.returncode,
                stdout,
                stderr)