"""
Abstract base class for things that need building.

These classes should be listed as the entry point [fassembler.project]
"""
import os
import sys
import re
from cStringIO import StringIO
from fassembler.namespace import Namespace
from fassembler.text import indent, underline, dedent
from cmdutils import CommandError
from tempita import Template

class Project(object):
    """
    This represents an abstract project.

    Subclasses should describe the project built in the docstring,
    and/or the title attribute.

    Subclasses should also define an actions attribute, which is a
    list of tasks, and a settings attribute, which is a list of
    Setting instances.

    Subclasses may set depends_on_projects to a list of strings that
    give projects that must be installed before installing this
    project.

    Subclasses may set depends_on_executables to a list of executables
    that must be found on $PATH in order for thisproject to be installed
    successfully. Each item in the list can be either a string or a list
    of strings; for example,
      depends_on_executables = ['wget', ('httpd', 'apache2')]
    will confirm that ``wget`` is found on $PATH, and that EITHER ``httpd``
    or ``apache2`` is found.
    """

    name = None
    title = None
    actions = None
    settings = []
    depends_on_projects = []
    # Set this to a list of executables that must be found; each item in the list
    # can be a list of options, e.g., [('apache2', 'httpd')]:
    depends_on_executables = []

    # Override spec_filename if you want to use another project's spec file to find req_settings.    
    spec_filename = None 


    def __init__(self, project_name, maker, environ, logger, config):
        self.project_name = project_name
        self.maker = maker
        self.environ = environ
        self.logger = logger
        self.config = config
        if self.name is None:
            raise NotImplementedError(
                "No name has been assigned to %r" % self)
        self.build_properties = {}

    @property
    def config_section(self):
        """
        The section that should be used to find settings for this project.
        """
        return self.name

    def confirm_settings(self, all_projects=None):
        """
        This is run to confirm that all the required settings have
        been set, for this project and all its tasks.
        """
        errors = []
        try:
            self.setup_config()
        except ValueError, e:
            errors.append(e)
        if self.depends_on_projects and all_projects is not None:
            for project in self.depends_on_projects:
                if (project not in all_projects
                    and not self.environ.is_project_built(project)):
                    errors.append('Project %s is not installed and is required' % project)
        for executables in self.depends_on_executables:
            if isinstance(executables, basestring):
                executables = [executables]
            try:
                self.confirm_on_path(*executables)
            except OSError, e:
                errors.append(str(e))
        return errors

    def run(self):
        """
        Actually run the project.  Subclasses seldom override this;
        this runs all the tasks given in ``self.actions``
        """
        if self.actions is None:
            raise NotImplementedError(
                "The actions attribute has not been overridden in %r"
                % self)
        self.setup_config()
        tasks = self.bind_tasks()
        for task in tasks:
            self.logger.set_section(self.name+'.'+task.name)
            self.logger.notify('== %s ==' % task.name, color='bold green')
            self.logger.indent += 2
            while 1:
                try:
                    try:
                        self.logger.debug('Task Plan:')
                        self.logger.debug(indent(str(task), '  '))
                        task.run()
                    finally:
                        self.logger.indent -= 2
                except (KeyboardInterrupt, CommandError):
                    raise
                except:
                    should_continue = self.maker.handle_exception(sys.exc_info(), can_continue=True,
                                                                  can_retry=True)
                    if should_continue == 'retry':
                        self.logger.notify('Retrying task %s' % task.name)
                        continue
                    if not should_continue:
                        self.logger.fatal('Project %s aborted.' % self.title, color='red')
                        raise CommandError('Aborted', show_usage=False)
                break
        self.environ.add_built_project(self.project_name)

    def bind_tasks(self):
        """
        Bind all the task instances to the context in which they will
        be run (with this project, the maker, etc).
        """
        tasks = []
        for task in self.iter_actions():
            task.bind(maker=self.maker, environ=self.environ,
                      logger=self.logger, config=self.config,
                      project=self)
            task.confirm_settings()
            task.setup_build_properties()
            tasks.append(task)
        return tasks

    def iter_actions(self, iter_from=None):
        """
        Yield all the actions, and sub-actions
        """
        if iter_from is None:
            iter_from = self.actions
        for task in iter_from:
            yield task
            for subtask in self.iter_actions(task.iter_subtasks()):
                yield subtask

    def make_description(self, tasks=None):
        """
        Returns the description of this project, in the context of the
        settings given.
        """
        self.setup_config()
        if tasks is None:
            tasks = self.bind_tasks()
        out = StringIO()
        title = self.title or self.name
        title = '%s (%s)' % (title, self.project_name)
        print >> out, underline(title)
        doc = self.__doc__
        if doc == Project.__doc__:
            doc = '[No project description set]'
        print >> out, dedent(doc)
        print >> out
        print >> out, indent(underline('Settings', '='), '  ')
        ns = self.create_namespace()
        if not self.settings:
            print >> out, indent('No settings', '    ')
        else:
            for setting in self.settings:
                try:
                    setting_value = getattr(ns['config'], setting.name)
                except Exception, e:
                    setting_value = 'Cannot calculate value: %s %s' % (e.__class__.__name__, e)
                print >> out, indent(setting.description(value=setting_value), '    ')
        print >> out
        print >> out, indent(underline('Tasks', '='), '  ')
        for task in tasks:
            desc = str(task)
            print >> out, indent(underline(task.title, '-'), '    ')
            print >> out, indent(desc, '    ')
            print >> out
        if self.depends_on_projects:
            print >> out, indent(underline('Dependencies', '='), '  ')
            for project in self.depends_on_projects:
                print >> out, indent('* %s' % project, '  ')
        return out.getvalue()

    def interpolate(self, string, stacklevel=1, name=None):
        """
        Interpolate a string in the context of the project namespace.
        """
        return self.interpolate_ns(string, self.create_namespace(), stacklevel=stacklevel+1, name=name)

    def interpolate_ns(self, string, ns, stacklevel=1, name=None):
        """
        Interpolate a string in the given namespace.
        """
        if string is None:
            return None
        if isinstance(string, (list, tuple)):
            new_items = []
            for item in string:
                new_items.append(self.interpolate_ns(item, ns, stacklevel+1, name=name))
            return new_items
        if isinstance(string, dict):
            new_dict = {}
            for key in string:
                new_dict[self.interpolate_ns(key, ns, stacklevel+1, name=name)] = self.interpolate_ns(
                    string[key], ns, stacklevel+1, name=name)
            return new_dict
        if not isinstance(string, Template):
            if not isinstance(string, basestring):
                # Not a template at all, don't substitute
                return string
            tmpl = Template(string, name=name, stacklevel=stacklevel+1)
        else:
            tmpl = string
        return ns.execute_template(tmpl)

    def create_namespace(self):
        """
        Create a namespace for this object.

        Each call returns a new namespace.  This namespace can be
        further augmented (as it is by tasks).
        """
        ns = Namespace(self.config_section)
        ns['env'] = self.environ
        ns['maker'] = self.maker
        ns['project'] = self
        ns['os'] = os
        ns['re'] = re
        ns.add_all_sections(self.config)
        ns['config'] = ns[self.config_section]
        return ns

    def setup_config(self):
        """
        This sets all the configuration values, using defaults when
        necessary, or a value from the global configuration.
        """
        if not self.config.has_section(self.config_section):
            self.config.add_section(self.config_section)
        for setting in self.settings:
            if (not self.config.has_option(self.config_section, setting.name)
                and not self.config.has_option('DEFAULT', setting.name)):
                if not setting.has_default(self.environ):
                    raise ValueError(
                        "The setting [%s] %s (%s) must be set.  Use \"%s=VALUE\" on the command-line to set it"
                        % (self.config_section, setting.name, setting.help, setting.name))
                default = setting.get_default(self.environ)
                if default is not None:
                    self.config.set(self.config_section, setting.name, default)

    def confirm_on_path(self, *executables):
        """
        This checks that one of the given executables is on $PATH
        somewhere, and raises an error if not.

        Call from confirm_settings
        """
        paths = os.environ['PATH'].split(os.path.pathsep)
        for executable in executables:
            for path in paths:
                full = os.path.join(path, executable)
                if os.path.exists(full):
                    self.logger.debug('Found %s in %s' % (executable, full))
                    return
        raise OSError(
            "Could not find any of executable(s) %s in PATH %s.\n"
            "Please ensure that you have the relevant packages installed,\n"
            "and/or add the relevant directory to your $PATH."
            % (', '.join(executables), os.environ['PATH']))

    _setting_re = re.compile(r'^(\w+)\s*=\s*(.*)$')

    @property
    def req_settings(self):
        """
        Reads settings from the requirements file in requirements/<self.spec_filename or self.name>-req.txt
        Returns a dictionary
        """
        
        spec_filename = self.maker.path('requirements/%s-req.txt' % (
            self.spec_filename or self.name))
        if not os.path.exists(spec_filename):
            self.logger.debug('No requirements file in %s' % spec_filename)
            return {}
        settings = {}
        f = open(spec_filename)
        in_setting = None
        for line in f:
            line = line.rstrip()
            if line.strip() != line and in_setting:
                # Continuation line
                cur = settings[in_setting]
                settings[in_setting] = cur + '\n' + line.strip()
                continue
            if not line or line.strip().startswith('#'):
                continue
            match = self._setting_re.search(line)
            if match:
                name = match.group(1)
                value = match.group(2)
                if name in settings:
                    settings[name] = settings[name] + '\n' + value
                else:
                    settings[name] = value
                in_setting = name
            else:
                in_setting = None
        f.close()
        return settings        

class Setting(object):
    """
    Instances of Setting describe one setting a project takes.

    Settings each have a name, and should have help.  They may have a
    default value; if none is given then the setting must be set by
    the user.

    If ``inherit_config`` is given with a value like
    ``('section_name', 'config_name')``, then the setting will inherit
    from that value in the global config if it is not given explicitly.
    """

    class _NoDefault(object):
        def __repr__(self):
            return '(no default)'
    NoDefault = _NoDefault()
    del _NoDefault

    def __init__(self, name, default=NoDefault, help=None, inherit_config=None):
        self.name = name
        self.default = default
        self.help = help
        self.inherit_config = inherit_config

    def has_default(self, environ):
        """
        Is there a default for this setting, given the environment and
        its global configuration?
        """
        if self.default is not self.NoDefault:
            return True
        if self.inherit_config is not None:
            if environ.config.has_option(*self.inherit_config):
                return True
        return False

    def get_default(self, environ):
        """
        Find the default value for this setting, given the environment
        and its global configuration.
        """
        if self.inherit_config and environ.config.has_option(*self.inherit_config):
            return environ.config.get(*self.inherit_config)
        if self.default is not self.NoDefault:
            return self.default
        assert 0, 'no default'

    def __str__(self):
        return self.description(value=self.default)
        
    def description(self, value=None):
        msg = '%s:' % self.name
        msg += '\n  Default: %s' % self.description_repr(self.default)
        if value != self.default:
            msg += '\n  Value:   %s' % self.description_repr(value)
        if self.help:
            msg += '\n'+indent(self.help, '    ')
        return msg
        
    def description_repr(self, value):
        if isinstance(value, basestring):
            if value == '':
                return "''"
            if value.strip() != value or value.strip('"\'') != value:
                return repr(value)
            if isinstance(value, unicode):
                value = value.encode('unicode_escape')
            else:
                value = value.encode('string_escape')
            return value
        return repr(value)
            
        
