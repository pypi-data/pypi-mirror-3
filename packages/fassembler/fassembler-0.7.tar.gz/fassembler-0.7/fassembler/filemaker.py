"""
The basic abstraction for doing actions.

Everything happens in the Maker object.
"""
# (c) 2005 Ian Bicking, Ben Bangert, and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# This was originally based on paste.filemaker
import os
import re
import shutil
import string
import subprocess
import sys
import tempfile
import tempita
import util

from difflib import unified_diff, context_diff
from environ import random_string
from getpass import getpass

EXE_MODE = 0111

class RunCommandError(OSError):
    """
    Represents a failed script run (a script that returns a non-zero
    exit code, and/or has output on stderr).
    """
    def __init__(self, message, command=None, stdout=None, stderr=None, returncode=None):
        OSError.__init__(self, message)
        self.command = command
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode

    def __str__(self):
        return '%s running %s (code: %s)' % (self.args[0],
                                             self.command,
                                             self.returncode)

class Maker(object):
    """
    Instances of Maker are abstractions of several pieces of context:

    * The base_path, the implement root of all destination file paths
    * A logger
    * A simulate flag (if true, then nothing should *actually* be done)
    * An interactive flag (if true, then query the user about some changes)
    * A quick flag (if true, skip some checks to make this run faster)

    All actions should ideally go through this object.

    This object is generally instantiated just once per fassembler
    run, and used by all projects and tasks.
    """
    
    def __init__(self, base_path, logger,
                 simulate=False, 
                 interactive=True,
                 quick=False,
                 beep=False):
        """
        Initialize the Maker.  Files go under base_path.
        """
        self.base_path = self._normpath(base_path)
        self.logger = logger
        self.simulate = simulate
        self.interactive = interactive
        self.quick = quick
        self.beep = beep
    
    def copy_file(self, src, dest=None, dest_dir=None, template_vars=None,
                  interpolater=None, overwrite=False, svn_add=True):
        """
        Copy a file from the source location to somewhere in the
        destination.

        If the file ends with _tmpl, then that suffix will be removed
        and the file will be filled as a template.  You must provide
        template_vars in this case.
        """
        assert not dest or not dest_dir
        assert dest or dest_dir
        if dest_dir:
            dest = os.path.join(dest_dir, os.path.basename(src))
        if dest.endswith('_tmpl'):
            dest = dest[:-5]
        dest = self.path(dest)
        src = self.path(src)
        self._warn_filename(dest)
        contents, raw_contents = self._get_contents(src, template_vars, interpolater)
        overwrite = False
        if os.path.exists(dest):
            existing = self._get_raw_contents(dest)
            base_content = self._get_base_contents(dest)
            if existing == contents:
                self.logger.info('File %s exists with same content' % self.display_path(dest))
            elif base_content and existing == base_content:
                # logging happens in ensure_file
                pass
            else:
                message = 'File %s already exists (with different content)' % self.display_path(dest)
                if os.path.exists(self._orig_filename(dest)):
                    existing_raw = self._get_raw_contents(self._orig_filename(dest))
                    if existing_raw == raw_contents:
                        message = (
                            'File %s already exists (with different substitutions, but same original template)'
                            % self.display_path(dest))
                if self.interactive:
                    response = self.ask_difference(dest, message, contents, existing)
                    if not response:
                        self.logger.notify('Aborting copy')
                        return
                overwrite = True

        self.ensure_file(dest, contents, overwrite=overwrite, 
                         executable=os.stat(src).st_mode&0111, svn_add=svn_add)
        if contents != raw_contents:
            if not self.simulate:
                self.ensure_file(self._orig_filename(dest), raw_contents, overwrite=True,
                                 svn_add=svn_add, quiet=True)
                self.ensure_file(self._base_filename(dest), contents, overwrite=True,
                                 svn_add=svn_add, quiet=True)

    def _orig_filename(self, filename):
        """
        Gives the filename used to save the template used to generate a 'real' file.
        """
        return os.path.join(os.path.dirname(filename),
                            '.'+os.path.basename(filename)+'.orig')

    def _base_filename(self, filename):
        """
        Gives the filename used to save the text of a file (not the template, the filled in text).
        """
        return os.path.join(os.path.dirname(filename),
                            '.'+os.path.basename(filename)+'.base')

    def _get_contents(self, filename, template_vars=None, interpolater=None):
        """
        Return the (contents, raw_contents) of a file.

        If the file ends with ``_tmpl`` then it is assumed to be a
        Tempita template and substitution is done (if you give an
        interpolater callback, the interpolater is called like
        ``interpolater(raw_contents, template_Vars,
        filename=filename)``).

        If the file doesn't end with ``_tmpl``, then contents and
        raw_contents will be the same and no modification will be
        done.
        """
        is_tmpl = filename.endswith('_tmpl')
        if is_tmpl and template_vars is None and interpolater is None:
            raise ValueError(
                "You must provide template_vars to fill a file (filename=%r)"
                % filename)
        raw_contents = contents = self._get_raw_contents(filename)
        if is_tmpl:
            if interpolater is not None:
                contents = interpolater(contents, template_vars, filename=filename)
            else:
                contents = self.fill(contents, template_vars, filename=filename)
        return contents, raw_contents

    def _get_raw_contents(self, filename):
        """
        Return the contents of a file.
        """
        f = open(filename, 'rb')
        try:
            return f.read()
        finally:
            f.close()

    def _get_base_contents(self, filename):
        new_filename = self._base_filename(filename)
        if not os.path.exists(new_filename):
            return None
        return self._get_raw_contents(new_filename)

    def _writefile(self, filename, contents):
        """
        Write the contents to a file.
        """
        self.logger.debug('Writing %i bytes to %s' %
                          (len(contents), filename))
        f = open(filename, 'wb')
        f.write(contents)
        f.close()

    def fill(self, contents, template_vars, filename=None):
        """
        Fill the content as a template, using the given variables.
        """
        tmpl = tempita.Template(contents, name=filename)
        return tmpl.substitute(template_vars)

    def path(self, path):
        """
        Returns a normalized path, interpreted as relative to
        ``self.base_path``
        """
        assert isinstance(path, basestring), "Bad path: %r" % (path, )
        return self._normpath(os.path.join(self.base_path, path))

    def display_path(self, path):
        """
        Return the path, possibly shortened for display purposes.

        This strips ``self.base_path`` from the filename, if necessary.
        """
        path = self._normpath(path)
        if path.startswith(self.base_path):
            path = path[len(self.base_path):].lstrip(os.path.sep)
        return path

    def _warn_filename(self, filename):
        """
        Issues a warning if the filename is outside base_path
        """
        filename = self._normpath(filename)
        if not filename.startswith(self.base_path):
            self.logger.warn('Writing to file outside base directory: %s' % filename)

    def _normpath(self, path):
        """
        A more thorough normalization of a path than just what ``os.path.normpath`` does.
        """
        assert isinstance(path, basestring), "Bad path: %r" % (path, )
        path = os.path.expanduser(path)
        return os.path.normcase(os.path.abspath(path))
    
    def copy_dir(self, src, dest, sub_filenames=True, template_vars=None, interpolater=None, include_hidden=False,
                 add_dest_to_svn=False):
        """
        Copy a directory recursively (from ``src`` to ``dest``),
        processing any files within it that need to be processed (end
        in _tmpl).

        If ``include_hidden`` is False, then 'hidden' files (files
        with a leading dot) will be skipped.

        If ``sub_filenames`` is true, then ``+var+`` in filenames will
        be replaced with the value of variables from
        ``template_vars``.

        If ``interpolater`` is given, that is a callback that will be
        used with ``self._get_contents`` to fill in template files.

        If ``add_dest_to_svn`` is true, then if ``dest`` is contained
        in an svn-controlled directory it will be added to that
        directory.
        """
        if template_vars is None:
            sub_filenames = False
        skips = []
        dest = self.path(dest)
        self.ensure_dir(dest, svn_add=add_dest_to_svn)
        for dirpath, dirnames, filenames in os.walk(src):
            ## FIXME: this doesn't indent or handle recursion as
            ## cleaning as a trully recursive version would.
            dirnames.sort()
            filenames.sort()
            if not include_hidden and self.is_hidden(dirpath):
                skips.append(dirpath)
                continue
            parent_hidden = False
            for skip in skips:
                if dirpath.startswith(skip):
                    parent_hidden = True
                    break
            if parent_hidden:
                continue
            assert dirpath.startswith(src)
            dirpath = dirpath[len(src):].lstrip(os.path.sep)
            for dirname in dirnames:
                if not include_hidden and self.is_hidden(dirname):
                    self.logger.debug('Skipping hidden directory %s' % dirname)
                    continue
                destdir = self.path(os.path.join(dest, dirpath, dirname))
                if sub_filenames:
                    orig_destdir = destdir
                    destdir = self.fill_filename(destdir, template_vars)
                    if orig_destdir != destdir:
                        self.logger.debug('Filling name %s to %s' % (orig_destdir, destdir))
                self.ensure_dir(destdir)
            for filename in filenames:
                if not include_hidden and self.is_hidden(filename):
                    self.logger.debug('Skipping hidden file %s' % filename)
                    continue
                destfn = self.path(os.path.join(dest, dirpath, filename))
                if sub_filenames:
                    orig_destfn = destfn
                    destfn = self.fill_filename(destfn, template_vars)
                    if orig_destfn != destfn:
                        self.logger.debug('Filling name %s to %s' % (orig_destfn, destfn))
                self.copy_file(os.path.join(src, dirpath, filename), destfn, template_vars=template_vars, interpolater=interpolater)

    def is_hidden(self, filename):
        return os.path.basename(filename).startswith('.')

    _filename_var_re = re.compile(r'[+](.*?)[+]')

    def fill_filename(self, filename, template_vars):
        """
        Fills a filename with the given variables.

        Anything like ``+var+`` will be treated as a substitution in
        the filename.

        The special variables ``+dot+`` and ``+plus+`` are available,
        the first for hidden files that you want to actually copy, the
        second for putting ``+`` in a filename.
        """
        vars = template_vars.copy()
        vars.setdefault('dot', '.')
        vars.setdefault('plus', '+')
        def subber(match):
            name = match.group(1)
            if name not in vars:
                raise NameError(
                    "Variable +%s+ not in variables, in filename %s"
                    % (name, filename))
            return vars[name]
        return self._filename_var_re.sub(subber, filename)

    def exists(self, path):
        """
        Does the path exist?  Paths are normalized against ``self.base_path``
        """
        return os.path.exists(self.path(path))
    
    def ensure_dir(self, dir, svn_add=True, package=False):
        """
        Ensure that the directory exists, creating it if necessary.
        Respects verbosity and simulation.

        Adds directory to subversion if ``.svn/`` directory exists in
        parent, and directory was created.
        
        package
            If package is True, any directories created will contain a
            __init__.py file.
        
        """
        dir = self.path(dir)
        dir = os.path.abspath(dir.rstrip(os.sep))
        if not dir:
            # we either reached the parent-most directory, or we got
            # a relative directory
            # @@: Should we make sure we resolve relative directories
            # first?  Though presumably the current directory always
            # exists.
            return
        if not os.path.exists(dir):
            self.ensure_dir(os.path.dirname(dir), svn_add=svn_add, package=package)
            self.logger.notify('Creating %s' % self.display_path(dir))
            if not self.simulate:
                os.mkdir(dir)
            if (svn_add and
                os.path.exists(os.path.join(os.path.dirname(dir), '.svn'))):
                self.svn_command('add', dir)
            if package:
                initfile = os.path.join(dir, '__init__.py')
                f = open(initfile, 'wb')
                f.write("#\n")
                f.close()
                self.logger.notify('Creating %s' % self.display_path(initfile))
                if (svn_add and
                    os.path.exists(os.path.join(os.path.dirname(dir), '.svn'))):
                    self.svn_command('add', initfile)
        else:
            self.logger.debug("Directory already exists: %s" % self.display_path(dir))

    def ensure_file(self, filename, content, svn_add=True, package=False,
                    overwrite=False, executable=False, quiet=False):
        """
        Ensure a file named ``filename`` exists with the given
        content.  If ``--interactive`` has been enabled, this will ask
        the user what to do if a file exists with different content.
        """
        filename = self.path(filename)
        self.ensure_dir(os.path.dirname(filename), svn_add=svn_add, package=package)
        if not os.path.exists(filename):
            if not quiet:
                self.logger.info('Creating %s' % filename)
            if not self.simulate:
                f = open(filename, 'wb')
                f.write(content)
                f.close()
            if executable:
                self.make_executable(filename)
            if svn_add and os.path.exists(os.path.join(os.path.dirname(filename), '.svn')):
                self.svn_command('add', filename)
            return
        f = open(filename, 'rb')
        old_content = f.read()
        f.close()
        base_content = self._get_base_contents(filename)
        if content == old_content:
            if not quiet:
                self.logger.info('File %s matches expected content' % filename)
            if executable and not os.stat(filename).st_mode&0111:
                self.make_executable(filename)
            return
        show_overwrite_warning = True
        if base_content and base_content == old_content:
            if not quiet:
                self.logger.notify('File %s was not edited and content has changed, overwriting'
                                   % self.display_path(filename),
                                   color='cyan')
            show_overwrite_warning = False
        elif not overwrite:
            if not quiet:
                self.logger.notify('Warning: file %s does not match expected content' % filename)
            if self.interactive:
                response = self.ask_difference(filename, None, content, old_content)
                if not response:
                    return
            else:
                return

        if show_overwrite_warning:
            if not quiet:
                self.logger.notify('Overwriting %s with new content' % filename)
        if not self.simulate:
            f = open(filename, 'wb')
            f.write(content)
            f.close()
            if executable:
                self.make_executable(filename)

    def make_executable(self, filename):
        """
        Make a file executable.
        """
        self.logger.info('Making file %s executable' % filename)
        if not self.simulate:
            st_mode = os.stat(filename).st_mode
            st_mode |= 0111
            os.chmod(filename, st_mode)

    _svn_failed = False

    def svn_command(self, *args, **kw):
        """
        Run an svn command, but don't raise an exception if it fails.
        """
        try:
            return self.run_command('svn', *args, **kw)
        except OSError, e:
            if not self._svn_failed:
                self.logger.warn('Unable to run svn command (%s); proceeding anyway' % e)
                self._svn_failed = True

    def ensure_symlink(self, source, dest, overwrite=False):
        """
        Ensure that source is symlinked to dest.  If overwrite is
        false, and the symlink is wrong, correct it (otherwise ask).

        Even if overwrite is true, this will not overwrite
        non-symlinks.
        """
        source = self.path(source)
        dest = self.path(dest)
        assert source != dest, (
            "Symlink from %s to itself is wrong! (source==dest)" % source)
        if not os.path.exists(dest) and os.path.lexists(dest):
            # Sign of a broken symlink
            self.logger.info('Removing broken link %s' % dest)
            if not self.simulate:
                os.unlink(dest)
        if os.path.exists(dest) and overwrite:
            if os.path.islink(dest):
                # It's a symlink, and we should overwrite it
                self.logger.notify('Removing symlink %s (-> %s)'
                                   % (dest, os.path.realpath(dest)))
                if not self.simulate:
                    os.unlink(dest)
            else:
                self.logger.warn('Cannot remove symlink destination %s because it is not a symlink'
                                 % dest)
        if not os.path.exists(dest):
            self.logger.info('Symlinking %s to %s' % (source, dest))
            if not self.simulate:
                os.symlink(source, dest)
            return
        if os.path.realpath(dest) == source:
            self.logger.info('Symlink %s -> %s already exists and is correct' % (dest, source))
            return
        if os.path.islink(dest):
            msg = 'At %s there is a symlink from %s; it should be a symlink from %s' % (
                dest, os.path.realpath(dest), source)
        else:
            if os.path.isdir(dest):
                noun = 'directory'
            else:
                noun = 'file'
            msg = 'At %s there is a %s; this should be a symlink from %s' % (
                dest, noun, source)
        response = self.ask(
            msg,
            responses=['(i)gnore',
                       '(b)ackup',
                       '(w)ipe'],
            first_char=True)
        if response == 'i':
            self.logger.notify('Skipping symlinking %s to %s' % (source, dest))
            return
        elif response == 'b':
            self.backup(dest)
        elif response == 'w':
            if os.path.islink(dest):
                self.logger.notify('Removing symlink at %s' % dest)
                os.unlink(dest)
            else:
                self.logger.notify('Removing dir/file at %s' % dest)
                shutil.rmtree(dest)
        else:
            assert 0
        self.logger.info('Symlinking %s to %s' % (source, dest))
        if not self.simulate:
            os.symlink(source, dest)

    def rmtree(self, filename):
        """
        Deletes a tree recursively.
        """
        if not os.path.isdir(filename):
            self.logger.fatal('%s is not a directory' % filename)
            raise OSError('%s is not a directory' % filename)
        self.logger.debug('Deleting recursively: %s' % filename)
        if not self.simulate:
            shutil.rmtree(filename)

    def run_command(self, cmd, *args, **kw):
        """
        Runs the command (either a single string, or a script with
        arguments), respecting verbosity and simulation.  Returns
        stdout, or None if simulating.

        Some keyword arguments are supported:

        ``cwd``:
            The working directory to run the script in.  By default it
            is ``self.base_path``.

        ``stdin``:
            The text to pass in stdin.

        ``capture_stderr``:
            If true, then stderr is captured in stdout, instead of
            being handled separately.

        ``expect_returncode``:
            If true, then a non-zero exit code from the script will
            not be an error.

        ``return_full``:
            If true, then ``(stdout, stderr, returncode)`` is
            returned; otherwise by default only stdout is returned.

        ``extra_path``:
            A list of extra paths that should be added to ``$PATH``

        ``env``:
            The environment to run the script in (by default the same
            environment as this process is run in, os.environ).

        ``script_abspath``:
            If given, the script will be looked for in the given path
            exactly.  You can also just give an absolute path for the
            first argument.

        ``log_error``:
            If true (the default) then errors will be logged

        ``log_filter``:
            This is a function that takes a line of output from the
            program, and returns either a log level alone, or
            (new_line, level).  If not provided, then the output of
            the process will not be displayed.  You may also give an
            integer which will be the level of all output (e.g.,
            logger.INFO).

        ``shell``:
            Run the command string in a child shell. Default False.
        """
        cwd = popdefault(kw, 'cwd', self.base_path) or self.base_path
        cwd = self.path(cwd)
        if not os.path.exists(cwd):
            raise ValueError(
                "cwd for script (%r) does not exist" % cwd)
        capture_stderr = popdefault(kw, 'capture_stderr', False)
        expect_returncode = popdefault(kw, 'expect_returncode', False)
        return_full = popdefault(kw, 'return_full')
        extra_path = popdefault(kw, 'extra_path', [])
        env = popdefault(kw, 'env', os.environ)
        script_abspath = popdefault(kw, 'script_abspath', None)
        log_error = popdefault(kw, 'log_error', True)
        simulate = popdefault(kw, 'simulate', self.simulate)
        stdin = popdefault(kw, 'stdin', None)
        log_filter = popdefault(kw, 'log_filter', None)
        use_shell = popdefault(kw, 'shell', False)
        if extra_path:
            env = env.copy()
            path_parts = env.get('PATH', '').split(os.path.pathsep)
            env['PATH'] = os.path.pathsep.join(extra_path + path_parts)
        if script_abspath:
            cmd = self._script_abspath(cmd, script_abspath)
        assert not kw, ("Arguments not expected: %s" % kw)
        if capture_stderr or log_filter:
            stderr_pipe = subprocess.STDOUT
        else:
            stderr_pipe = subprocess.PIPE
        if args:
            cmd = [cmd] + list(args)
        if stdin:
            stdin_argument = subprocess.PIPE
        else:
            stdin_argument = None
        try:
            proc = subprocess.Popen(cmd,
                                    cwd=cwd,
                                    env=env,
                                    stdin=stdin_argument,
                                    stderr=stderr_pipe,
                                    stdout=subprocess.PIPE,
                                    shell=use_shell)
        except OSError, e:
            if e.errno != 2:
                # File not found
                raise
            raise OSError(
                "The expected executable %s was not found (%s)"
                % (cmd, e))
        self.logger.info('Running %s (PID %s)' % (self._format_command(cmd),
                                                  proc.pid))
        if env != os.environ:
            self.logger.debug('Using environment overrides: %s' % dict_diff(env, os.environ))
        if cwd != self.base_path:
            self.logger.debug('Running in working directory %s' % self.display_path(cwd))
        if simulate:
            if return_full:
                return (None, None, 0)
            else:
                return None
        if stdin:
            proc.stdin.write(stdin)
        if log_filter:
            stdout = []
            stdout_pipe = proc.stdout
            while 1:
                line = stdout_pipe.readline()
                if not line:
                    break
                stdout.append(line)
                line = line.rstrip()
                if isinstance(log_filter, int):
                    level = log_filter
                else:
                    level = log_filter(line)
                if isinstance(level, tuple):
                    line, level = level
                if line:
                    self.logger.log(level, line)
                if not self.logger.stdout_level_matches(level):
                    self.logger.show_progress()
            stdout = ''.join(stdout)
            stderr = ''
            # Bug #2128: The return code isn't set just by reading stdout;
            # you have to call wait() or communicate().
            proc.wait()
        else:
            stdout, stderr = proc.communicate()
        if proc.returncode and not expect_returncode:
            if log_error:
                self.logger.log(slice(self.logger.WARN, self.logger.FATAL),
                                'Running %s' % self._format_command(cmd), color='bold red')
                self.logger.warn('Error (exit code: %s)' % proc.returncode, color='bold red')
                if stdout:
                    self.logger.warn('stdout:')
                    self.logger.indent += 2
                    try:
                        self.logger.warn(stdout)
                    finally:
                        self.logger.indent -= 2
                if stderr:
                    self.logger.warn('stderr:')
                    self.logger.indent += 2
                    try:
                        self.logger.warn(stderr)
                    finally:
                        self.logger.indent -= 2
            raise RunCommandError("Error executing command %s (code %s)" %
                                  (self._format_command(cmd), proc.returncode),
                                  command=cmd, stdout=stdout, stderr=stderr,
                                  returncode=proc.returncode)
        if stderr:
            self.logger.debug('Command error output:\n%s' % stderr)
        if stdout:
            self.logger.debug('Command output:\n%s' % stdout)
        if return_full:
            return (stdout, stderr, proc.returncode)
        else:
            return stdout

    def _script_abspath(self, cmd, abspath):
        """
        Rewrite the command to use the given abspath
        """
        is_string = isinstance(cmd, basestring)
        if is_string:
            # Shell-style string command
            try:
                first, rest = cmd.split(None, 1)
            except ValueError:
                first = cmd
                rest = ''
        else:
            first, rest = cmd[0], cmd[1:]
        first = os.path.join(abspath, first)
        if is_string:
            if rest:
                return '%s %s' % (first, rest)
            else:
                return first
        else:
            return [first] + rest

    def _format_command(self, cmd):
        """
        Format a command for printing (turn a list of arguments into a string)
        """
        if not isinstance(cmd, list):
            return cmd
        def quote(item):
            if ' ' in item or '"' in item or "'" in item or '$' in item:
                item = item.replace('\\', '\\\\')
                item = item.replace('"', '\\"')
                item = item.replace('$', '\\$')
                item = item.replace("'", "\\'")
                return '"%s"' % item
            else:
                return item
        return ' '.join([quote(item) for item in cmd])

    def checkout_svn(self, repo, dest, revision=None):
        """
        Checkout an svn repository ``repo`` to the given ``dest`` path.

        If ``revision`` is given, it is used with ``svn checkout -r <revision>``.

        If the dest exists, this will check if the repository is the
        same one as is supposed to be checked out.  If not, the user
        will be asked about changing the repository (and may opt not
        to).  If ``self.quick`` is false, the repository will also be
        updated.
        """
        dest = self.path(dest)
        repo = repo.rstrip('/')
        if self.exists(dest):
            if self.quick:
                self.logger.notify('Checkout %s exists; skipping update' % dest)
                return
            current_repo = self._get_repo_url(dest)
            if current_repo:
                self.logger.debug('There is a repository at %s from %s'
                                  % (dest, current_repo))
            if current_repo and current_repo != repo:
                self.logger.debug("The repository at %s isn't from the expected location %s"
                                  % (dest, repo))
                if self.interactive:
                    response = self.ask(
                        'At %s there is already a checkout from %s\n'
                        'The expected repository is %s\n'
                        'What should I do?'
                        % (dest, current_repo, repo),
                        responses=['(i)gnore',
                                   '(s)witch',
                                   '(b)ackup',
                                   '(w)ipe'],
                        first_char=True)
                    if response == 'i':
                        self.logger.warn('Ignoring svn repository differences')
                    elif response == 's':
                        self.logger.warn('Switching repository locations')
                        self.run_command(
                            ['svn', 'switch', repo, dest])
                    elif response == 'b' or response == 'w':
                        if response == 'b':
                            self.backup(dest)
                        else:
                            self.logger.warn('Deleting checkout %s' % dest)
                        self.rmtree(dest)
                    else:
                        assert 0, response
        if self.exists(dest) and current_repo:
            cmd = ['svn', 'update']
            if revision:
                cmd.extend(['-r', str(revision)])
            cmd.append(dest)
            self.run_command(cmd)
            self.logger.notify('Updated repository at %s' % dest)
        else:
            ## FIXME: dot progress?
            cmd = ['svn', 'checkout']
            if revision:
                cmd.extend(['-r', str(revision)])
            cmd.extend([repo, dest])
            self.run_command(cmd, log_filter=self._filter_svn)
            self.logger.notify('Checked out repository to %s' % dest)

    def _filter_svn(self, line):
        """
        Filters svn output
        """
        if line: pass
        # @@

    _repo_url_re = re.compile(r'^URL:\s+(.*)$', re.MULTILINE)

    def _get_repo_url(self, path):
        """
        Get the subversion URL that path was checked out from
        """
        ## FIXME: ideally we'd set LANG or something, as the output
        ## can get i18n'd
        try:
            stdout = self.run_command(
                ['svn', 'info', path],
                log_error=False,
                simulate=False)
        except RunCommandError, e:
            if 'is not a working copy' in e.stderr:
                # Not really a problem
                return None
            if 'no es una copia de trabajo' in e.stderr:
                return None
            raise
        match = self._repo_url_re.search(stdout)
        if not match:
            raise ValueError(
                "Could not determine svn URL of %s; output:\n%s"
                % (path, stdout))
        return match.group(1).strip().rstrip('/')

    all_answer = None

    def colorize_diff(self, text):
        """Colorize a diff for output on a terminal, if possible.
        """
        if not self.logger.supports_color(sys.stdout):
            return text
        try:
            from pygments import highlight, lexers, formatters
        except ImportError:
            return text
        return highlight(text, lexers.get_lexer_by_name('diff'),
                         formatters.get_formatter_by_name('terminal'))

    def ask_difference(self, dest_fn, message, new_content, cur_content):
        """
        Ask about the differences between two files, and whether the
        old content should be overwritten.

        This returns true if the file should be overwritten, false
        otherwise.  It may backup the file if the user asks to do so.

        This gives the user an option to see a diff of the file.
        """
        u_diff = list(unified_diff(
            cur_content.splitlines(),
            new_content.splitlines(),
            dest_fn+' (old content)', dest_fn+' (new content)'))
        u_diff = [line.rstrip() for line in u_diff]
        c_diff = list(context_diff(
            cur_content.splitlines(),
            new_content.splitlines(),
            dest_fn+' (old content)', dest_fn+' (new content)'))
        c_diff = [line.rstrip() for line in c_diff]
        added = len([l for l in u_diff if l.startswith('+')
                       and not l.startswith('+++')])
        removed = len([l for l in u_diff if l.startswith('-')
                       and not l.startswith('---')])
        if added > removed:
            msg = '; %i lines added' % (added-removed)
        elif removed > added:
            msg = '; %i lines removed' % (removed-added)
        else:
            msg = ''
        self.logger.notify(
            'Replace %i bytes with %i bytes (%i/%i lines changed%s)' % (
            len(cur_content), len(new_content),
            removed, len(cur_content.splitlines()), msg))
        if message:
            print message
        prompt = 'Overwrite %s [y/n/d/b/m/?] ' % dest_fn
        prompt = self.logger.colorize(prompt, 'bold cyan')
        while 1:
            if self.all_answer is None:
                self.beep_if_necessary()
                response = raw_input(prompt).strip().lower()
            else:
                response = self.all_answer
            if not response or response[0] == 'b':
                import shutil
                new_dest_fn = dest_fn + '.bak'
                n = 0
                while os.path.exists(new_dest_fn):
                    n += 1
                    new_dest_fn = dest_fn + '.bak' + str(n)
                self.logger.notify('Backing up %s to %s' % (dest_fn, new_dest_fn))
                if not self.simulate:
                    shutil.copyfile(dest_fn, new_dest_fn)
                return True
            elif response.startswith('all '):
                rest = response[4:].strip()
                if not rest or rest[0] not in ('y', 'n', 'b'):
                    print self.query_usage
                    continue
                response = self.all_answer = rest[0]
            if response[0] == 'y':
                return True
            elif response[0] == 'n':
                return False
            elif response == 'dc':
                print self.colorize_diff('\n'.join(c_diff))
            elif response[0] == 'd':
                print self.colorize_diff('\n'.join(u_diff))
            elif response[0] == 't':
                # Hidden feature
                import traceback
                traceback.print_stack()
                continue
            elif response == 'm':
                if self.merge_difference(dest_fn, new_content, cur_content):
                    return False
                else:
                    self.logger.error('An error was encountered while trying to merge the two files')
            else:
                if response[0] != '?':
                    print 'Unknown command: %s' % response
                print self.query_usage

    query_usage = '''\
Responses:
  Y(es):    Overwrite the file with the new content.
  N(o):     Do not overwrite the file.
  D(iff):   Show a unified diff of the proposed changes (dc=context diff)
  B(ackup): Save the current file contents to a .bak file
            (and overwrite)
  M(erge):  Perform a side-by-side merge of the affected files
  Type "all Y/N/B/M" to use Y/N/B/M for answer to all future questions
'''

    def merge_difference(self, dest_fn, new_content, cur_content):
        """
        Take changed contents, and a destination filename, and performs a side
        by side merge using sdiff
        """
        # In order to ensure that we don't leak temporary files, we perform
        # this in three stages, creation, setup, and working with the files.

        # Phase 1: Temporary file creation
        # If this fails, we'll close and delete any files that did succeed
        try:
            orig_fd, orig_name = tempfile.mkstemp(prefix=dest_fn + '_orig_')
        except:
            return False
        try:
            new_fd, new_name = tempfile.mkstemp(prefix=dest_fn + '_new_')
        except:
            os.close(orig_fd)
            os.unlink(orig_name)
            return False

        # Phase 2: write out the content
        # If there is some sort of failure, we'll close and delete the files we
        # created in phase 1
        try:
            try:
                os.write(orig_fd, cur_content)
                os.write(new_fd, new_content)
            finally:
                os.close(orig_fd)
                os.close(new_fd)
        except:
            os.unlink(orig_name)
            os.unlink(new_name)
            return False

        # Phase 3: working with the files
        # No matter what happens here, we'll be sure to remove the temporary
        # files before returning
        try:
            try:
                proc = subprocess.Popen(["sdiff", "-s", "-o", dest_fn, orig_name, new_name])
                proc.wait()
                return True
            finally:
                os.unlink(orig_name)
                os.unlink(new_name)
        except:
            return False

    def ask_password(self, prompt="Input a password or press enter to generate a random one: "):
        """
        Prompt user to input a password.
        """
        def validate(pw):
            if pw[-1] == '$':
                # Don't end with $; this confuses zopectl
                raise ValueError('Password should not end with "$"')
            if pw[0] not in string.ascii_letters + string.digits:
                # Don't start with special characters; if the
                # generated password starts with "__", it breaks
                # Twill.parse.  (odds of this happening were 1/4356)
                raise ValueError(
                    'Password should not start with special chars')

        def randpw():
            while True:
                pw = random_string(12, string.ascii_letters + string.digits + "_-!;")
                try:
                    validate(pw)
                except ValueError:
                    continue
                return pw
            
        if not self.interactive:
            return randpw()
        self.beep_if_necessary()
        prompt2 = 'Confirm:'
        if self.logger.supports_color(sys.stdout):
            prompt, prompt2 = [self.logger.colorize(p, 'bold cyan') for p in prompt, prompt2]
        for i in range(3):
            inputpw = getpass(prompt).strip()
            if not inputpw:
                self.logger.info('Using randomly generated password')
                return randpw()
            if inputpw:
                # would be nicer UI if this wasn't a hard error, but
                # this is probably good enough.
                validate(inputpw)
            inputpw2 = getpass(prompt2).strip()
            if inputpw == inputpw2:
                return inputpw
        raise ValueError('Passwords did not match after 3 attempts')

    def ask(self, message, help=None, responses=['y', 'n'], default=None,
            first_char=False):
        """
        Ask something, using message to say what.
        If we're not running interactively, just return default.

        Responses are a list of the available responses, all lower
        case.  default, if given, is the default response if the user
        just presses enter.

        help is text that will be displayed if an erroneous input is given.

        If first_char is true, then only the first character of a
        response is necessary.  You may use things like
        ``['(b)ackup']`` in this case (parenthesis will be stripped).
        """
        if not self.interactive:
            return default
        responses = [res.lower() for res in responses]
        msg_responses = list(responses)
        if default:
            msg_responses.remove(default)
            msg_responses.insert(0, default.upper())
        if help and '?' not in responses:
            msg_responses.append('?')
        msg_responses = '/'.join(msg_responses)
        full_message = '%s [%s] ' % (message, msg_responses)
        if self.logger.supports_color(sys.stdout):
            full_message = self.logger.colorize(full_message, 'bold cyan')
        if first_char:
            responses = [res.strip('()')[0] for res in responses]
        while 1:
            self.beep_if_necessary()
            while 1:
                try:
                    response = raw_input(full_message).strip().lower()
                except EOFError:
                    # This can happen when a user hits ^Z
                    continue
                break
            if not response:
                if default:
                    if first_char:
                        return default.strip('()')[0]
                    return default
                else:
                    print 'Please enter a response (one of %s)' % msg_responses
                    continue
            if first_char:
                response = response[0]
            if response in responses:
                return response
            if response != '?':
                print 'Invalid response; please enter one of %s' % msg_responses
            if help:
                print help

    def beep_if_necessary(self):
        """
        Beep if --beep was given
        """
        if self.beep:
            sys.stdout.write(chr(7))
            sys.stdout.flush()
            
    def handle_exception(self, exc_info, can_continue=False, can_retry=False):
        """
        Give an interactive way to handle an exception.

        If can_continue is true, then the user is given the option to
        quit (abort the whole thing) or continue.  Not everything can
        be continued.

        If can_retry is true, then the user is given a retry option, and
        if they select it then this method returns the string 'retry'.
        It is up to the caller to actually retry.
        """
        self.logger.fatal('Error: %s' % exc_info[1], color='bold red')
        if not self.interactive:
            raise exc_info[0], exc_info[1], exc_info[2]
        responses = ['(t)raceback', '(q)uit']
        if can_continue:
            responses.append('(c)ontinue')
        if can_retry:
            responses.append('(r)etry')
        if self.logger.section:
            length = len(self.logger._section_logs)
            if length:
                responses.append('(v)iew logs (%s)' % length)
                responses.append('(p)aged view of logs')
        while 1:
            try:
                response = self.ask('What now?', responses=responses,
                                    first_char=True)
            except KeyboardInterrupt:
                print '^C'
                response = 'q'
            ## FIXME: maybe some fancy evalexception stuff?
            if response == 't':
                import traceback
                traceback.print_exception(*exc_info)
            elif response == 'c':
                return True
            elif response == 'q':
                return False
            elif response == 'r':
                return 'retry'
            elif response == 'v':
                print self.logger.section_text()
            elif response == 'p':
                pager = os.environ.get('PAGER', 'less')
                proc = subprocess.Popen(pager,
                                        stdin=subprocess.PIPE)
                proc.communicate(self.logger.section_text(color=False))
            else:
                assert 0

    def retrieve(self, url, filename):
        """Download a file and store it at filename.
        Depends on wget because urllib isn't reliable enough with large files
        and real networks.
        """
        self.run_command(['wget', '--no-check-certificate', url, '-O', filename])

    def backup(self, filename):
        """
        Moves the filename (file or directory) to a new location,
        adding a .bak, .bak2, etc to the name to move it aside.
        """
        n = 1
        ext = '.bak'
        while os.path.exists(filename + ext):
            n += 1
            ext = '.bak%s' % n
        self.logger.notify('Backing up %s to %s' % (filename, filename + ext))
        if not self.simulate:
            if os.path.isdir(filename):
                shutil.copytree(filename, filename+ext)
            else:
                shutil.copy2(filename, filename+ext)

def popdefault(dict, name, default=None):
    """
    Used to handle keyword-only arguments.
    """
    if name not in dict:
        return default
    else:
        v = dict[name]
        del dict[name]
        return v

def dict_diff(d1, d2):
    """
    Show the differences in two dictionaries (typically
    os.environ-style dicts).  Returns a human-readable string.
    """
    all_keys = sorted(set(d1) | set(d2))
    lines = []
    for key in all_keys:
        if key in d1 and key not in d2:
            lines.append('+%s=%r' % (key, d1[key]))
        elif key in d2 and key not in d1:
            lines.append('-%s (previously: %r)' % (key, d2[key]))
        elif d1[key] != d2[key]:
            lines.append('%s=%r (previously: %r)' % (key, d1[key], d2[key]))
    return '\n'.join(lines)
        
