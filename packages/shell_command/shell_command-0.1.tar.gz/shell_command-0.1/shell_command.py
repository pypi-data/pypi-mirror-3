"""shell_command - system shell invocation helpers
"""
import string
import shlex
import subprocess
import select

import sys
_is_py3_or_later = sys.version_info[0] >= 3


try:
    _shlex_quote = shlex.quote
except AttributeError:
    # Backport from Python 3.x. This suite is accordingly under the PSF
    # License rather than the BSD license used for the rest of the code.
    import re
    _find_unsafe = re.compile(r'[^\w@%+=:,./-]').search
    def _shlex_quote(s):
        """Return a shell-escaped version of the string *s*."""
        if not s:
            return "''"
        if _find_unsafe(s) is None:
            return s

        # use single quotes, and put single quotes into double quotes
        # the string $'b is then quoted as '$'"'"'b'
        return "'" + s.replace("'", "'\"'\"'") + "'"


class _ShellFormatter(string.Formatter):
    """Formatter to automatically escape interpolated values
    
       It is not thread safe due to the way it handles auto field numbering
    """
    def __init__(self):
        self._next_field = 0

    def vformat(self, fmt, args, kwds):
        return super(_ShellFormatter, self).vformat(fmt, args, kwds)

    def get_value(self, key, args, kwds):
        if key == '':
            key = self._next_field
            self._next_field += 1
        return super(_ShellFormatter, self).get_value(key, args, kwds)

    def convert_field(self, value, conversion):
        if conversion == 'u':
            return value
        elif conversion is None:
            return _shlex_quote(str(value))
        return super(_ShellFormatter, self).convert_field(value, conversion)


class ShellCommand(object):
    """ShellCommand accepts a command string and Popen constructor arguments.
    
    When initialised with an existing ShellCommand object, a new copy is
    made with the original Popen arguments updated with any new arguments.
    
    Method arguments are interpolated into the command string using
    str.format() style processing. All method arguments are coerced to strings
    and escaped using shlex.quote() by default, use the custom conversion
    specifier "!u" (for "unquoted") or any of the standard conversion
    specifiers (such as "!s") to bypass this quoting process.

    As brace characters ('{' and '}') in the command string are used to
    indicate interpolated fields, they must either be included in an
    interpolated value or else doubled (i.e. '{{' and '}}') in the format
    string in order to be passed to the underlying shell.
    
    The "shell" argument to Popen is enabled be default, but this can be
    overridden by explicitly setting it to False.
    In Python 3, the "universal_newlines" option is also enabled by default.
    """
    def __init__(self, command, **subprocess_kwds):
        if isinstance(command, ShellCommand):
            cmd = command.command
            kwds = command.subprocess_kwds.copy()
            kwds.update(subprocess_kwds)
        else:
            cmd = command
            kwds = subprocess_kwds
        kwds.setdefault("shell", True)
        if _is_py3_or_later:
            kwds.setdefault("universal_newlines", True)
        self.command = cmd
        self.subprocess_kwds = kwds

    def _kwds_repr(self):
        kwds = self.subprocess_kwds.copy()
        if kwds.get("shell", None):
            kwds.pop("shell")
        if _is_py3_or_later:
            if kwds.get("universal_newlines", None):
                kwds.pop("universal_newlines")
        if not kwds:
            return ''
        kwd_list = [""] + ["{}={!r}".format(k, v) for k, v in kwds.items()]
        return ','.join(kwd_list)
        
    def __repr__(self):
        name = type(self).__name__
        return "{}({!r}{})".format(name, self.command, self._kwds_repr())

    def format(self, *args, **kwds):
        """A str.format() variant for shell command interpolation.

        Refer to ShellCommand for details of the implicit quoting behaviour.
        """
        return _ShellFormatter().vformat(self.command, args, kwds)

    def format_map(self, mapping):
        """A str.format_map() variant for shell command interpolation.

        Refer to ShellCommand for details of the implicit quoting behaviour.
        """
        return _ShellFormatter().vformat(self.command, (), mapping)

    def shell_call(self, *args, **kwds):
        """A subprocess.call() variant for shell command invocation.

        Refer to ShellCommand for details of the implicit quoting behaviour.
        """
        cmd = _ShellFormatter().vformat(self.command, args, kwds)
        return subprocess.call(cmd, **self.subprocess_kwds)

    def check_shell_call(self, *args, **kwds):
        """A subprocess.check_call() variant for shell command invocation.

        Refer to ShellCommand for details of the implicit quoting behaviour.
        """
        cmd = _ShellFormatter().vformat(self.command, args, kwds)
        return subprocess.check_call(cmd, **self.subprocess_kwds)

    def shell_output(self, *args, **kwds):
        """A subprocess.check_output() variant for shell command invocation.

        Refer to ShellCommand for details of the implicit quoting behaviour.

        Use shell redirection (2>&1) to capture stderr in addition to stdout
        A trailing newline (if any) will be removed from the result

        As with subprocess.check_output(), this returns encoded bytes by
        default in Python 3. Passing "universal_newlines=True" in the
        constructor will also automatically decode the output to text with
        the UTF-8 codec. Alternatively, the result may be explicitly decoded
        after the call.
        """
        cmd = _ShellFormatter().vformat(self.command, args, kwds)
        data = subprocess.check_output(cmd, **self.subprocess_kwds)
        if data[-1:] == "\n":
            data = data[:-1]
        return data

    def iter_shell_output(self, *args, **kwds):
        """An alternative to shell_output() that yields output data as it
        becomes available.
        
        Since lines are made available as they are produced, the final line
        will still contain its terminating newline (if any).
        
        This operation relies on the use of select.select() on subrocess
        pipes, and hence is known to fail on Windows.
        """
        cmd = _ShellFormatter().vformat(self.command, args, kwds)
        popen_kwds = self.subprocess_kwds.copy()
        timeout = popen_kwds.pop("timeout", None)
        popen_kwds["stdout"] = subprocess.PIPE
        proc = subprocess.Popen(cmd, **popen_kwds)
        pipe = proc.stdout
        try:
            while 1:
                ready, __, done = select.select([pipe], (), [pipe], timeout)
                # Check for child process termination
                if done:
                    retcode = proc.poll()
                    if not retcode:
                        ready, __, __ = select.select([pipe], (), (), 0)
                        for line in pipe:
                            if line: 
                                yield line
                        break
                    raise subprocess.CalledProcessError(retcode, cmd)
                # Check for timeout
                if not ready:
                    proc.kill()
                    raise subprocess.TimeoutExpired(proc.args, timeout)
                # Read the next line from the pipe
                try:
                    line = pipe.read()
                except:
                    proc.kill()
                    proc.wait()
                    raise
                # Check for EOF from the pipe
                if line:
                    yield line
                else:
                    retcode = proc.wait()
                    if retcode:
                        raise subprocess.CalledProcessError(retcode, cmd)
                    break
        finally:
            pipe.close()

# Also provide module level convenience functions

def _copy_doc(source):
    """Decorator to copy docstrings"""
    def deco(f):
        f.__doc__ = source.__doc__
        return f
    return deco

@_copy_doc(ShellCommand.shell_call)
def shell_call(command, *args, **kwds):
    return ShellCommand(command).shell_call(*args, **kwds)

@_copy_doc(ShellCommand.check_shell_call)
def check_shell_call(command, *args, **kwds):
    return ShellCommand(command).check_shell_call(*args, **kwds)

@_copy_doc(ShellCommand.shell_output)
def shell_output(command, *args, **kwds):
    return ShellCommand(command).shell_output(*args, **kwds)

@_copy_doc(ShellCommand.iter_shell_output)
def iter_shell_output(command, *args, **kwds):
    return ShellCommand(command).iter_shell_output(*args, **kwds)

