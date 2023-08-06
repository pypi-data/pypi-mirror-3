"""
General TOPP-related projects, for the initial setup of the
environment.
"""

import os
import re
import socket
from cmdutils import CommandError
from fassembler.project import Project, Setting
from fassembler import tasks

class CheckBasePorts(tasks.Task):

    description = """
    Check that the ports {{task.base_port}} - {{int(task.base_port)+int(task.port_range)}} are open
    """

    base_port = tasks.interpolated('base_port')

    port_range = 22

    def __init__(self, name='Check base ports', base_port='{{config.base_port}}',
                 stacklevel=1):
        super(CheckBasePorts, self).__init__(name, stacklevel=stacklevel+1)
        self.base_port = base_port

    def run(self):
        base_port = int(self.base_port)
        port_range = int(self.port_range)
        self.logger.info('Checking ports %s-%s' % (base_port, base_port+port_range))
        bad = []
        for port in range(base_port, base_port+port_range+1):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('127.0.0.1', port))
            except socket.error, e:
                self.logger.info('Cannot bind port %s: %s' % (port, e))
                bad.append(port)
            else:
                sock.close()
        if bad:
            msg = 'Cannot bind to port(s): %s' % ', '.join(map(str, bad))
            self.logger.warn(msg)
            response = self.maker.ask('Continue despite unavailable ports?')
            if response == 'y':
                return
            raise CommandError(msg, show_usage=False)
        else:
            self.logger.info('All ports worked')

class DeleteBuildIniIfNecessary(tasks.Task):

    description = """
    If this is a fresh build from fassembler-boot, delete the empty build.ini file
    """

    def __init__(self, name='Delete fassembler-boot build.ini', stacklevel=1):
        super(DeleteBuildIniIfNecessary, self).__init__(name, stacklevel=stacklevel+1)

    def run(self):
        base_dir = self.maker.path('etc/')
        if os.path.exists(base_dir) and not os.path.exists(os.path.join(base_dir, '.svn')):
            build_ini = os.path.join(base_dir, 'build.ini')
            stat = os.stat(build_ini)
            if self.maker.simulate:
                self.logger.notify('Would delete %s' % build_ini)
                return
            if stat.st_size:
                response = self.maker.ask('build.ini is in the way of a checkout, but contains information.  Delete?', default='n')
                if response == 'n':
                    raise AssertionError(
                        "Cannot continue; %s exists (must be resolved manually)" % build_ini)
            else:
                self.logger.info('%s exists but is empty; deleting' % build_ini)
                os.unlink(build_ini)

class EnvironRefresh(tasks.Task):

    description = """
    Update configuration from {{env.config_filename}} if necessary
    """

    def __init__(self, name='Refresh environ', stacklevel=1):
        super(EnvironRefresh, self).__init__(name, stacklevel=stacklevel+1)

    def run(self):
        self.environ.refresh_config()



class EnsureAdminFile(tasks.EnsureFile):

    password = ''
    
    def __init__(self, name):
        super(EnsureAdminFile, self).__init__(
            name, '{{env.config.get("general", "admin_info_filename")}}',
            content='admin:{{task.password}}\n', overwrite=False)

    def run(self):
        if os.path.exists(self.dest):
            self.password = self.environ.parse_auth(self.dest).password
        else:
            self.password = self.environ.maker.ask_password()
        super(EnsureAdminFile, self).run()


def validate_db_prefix(prefix):
    if re.search(r'\W+', prefix):
        raise ValueError(
            "db_prefix can only contain letters, numbers, underscores; got %r"
            % prefix)
    
def validate_num_extra_zopes(num):
    try:
        int(num)
    except:
        raise ValueError(
            "num_extra_zopes must be an integer; got %s" % num)

class ToppProject(Project):
    """
    Create the basic layout used at TOPP for a set of applications.
    """

    name = 'topp'
    title = 'TOPP (openplans.org) Standard File Layout'
    project_base_dir = os.path.join(os.path.dirname(__file__), 'topp-files')

    settings = [
        Setting('requirements_svn_repo',
                inherit_config=('general', 'requirements_svn_repo'),
                default='https://svn.socialplanning.org/svn/build/requirements/openplans/trunk',
                help="Location where requirement files will be found for all builds"),
        Setting('requirements_use_wget',
                default='0'),
        Setting('base_port',
                inherit_config=('general', 'base_port'),
                help='The base port to use for application (each application is an offset from this port)'),
        Setting('var',
                default='{{env.base_path}}/var',
                inherit_config=('general', 'var'),
                help='The location where persistent files (persistent across builds) are kept'),
        Setting('etc_svn_repo',
                inherit_config=('general', 'etc_repository'),
                default='https://svn.openplans.org/config/',
                help='Parent directory where the configuration that will go in etc/ comes from'),
        Setting('etc_svn_subdir',
                default='{{env.hostname}}-{{os.path.basename(env.base_path)}}',
                inherit_config=('general', 'etc_svn_subdir'),
                help='svn subdirectory where data configuration is kept (will be created if necessary)'),
        Setting('db_prefix',
                default='{{re.sub(r"\W+", "_", os.path.basename(env.base_path))}}_',
                inherit_config=('general', 'db_prefix'),
                help='The prefix to use for all database names'),
        Setting('find_links',
                default='http://dist.socialplanning.org/eggs',
                help='Custom locations for distutils and easy_install to look in'),
        Setting('projtxt',
                default='{{project.req_settings.get("projtxt", "project")}}',
                help='Displayed name for opencore project/group'),
        Setting('projprefs',
                default='{{project.req_settings.get("projprefs", "Preferences")}}',
                help='Displayed name for opencore project/group settings'),
        Setting('localbuild',
                inherit_config=('general', 'localbuild'),
                default='False',
                help="Specifies whether this is a single developer's build"),
        Setting('num_extra_zopes',
                inherit_config=('general', 'num_extra_zopes'),
                default='0',
                help="How many additional Zope instances (besides the primary instance) are deployed in this stack"),
        Setting('spec',
                default='requirements/fassembler-req.txt',
                help="Requirements profile for any add-on packages to install in " \
                    "the Fassembler environment, providing additional build projects"),
        ]

    actions = [        
        CheckBasePorts(),
        tasks.CopyDir('Create layout', os.path.join(project_base_dir, 'base-layout'), './'),
        DeleteBuildIniIfNecessary(),
        tasks.SvnCheckout('Check out etc/', '{{config.etc_svn_subdir}}',
                          'etc/',
                          base_repository='{{config.etc_svn_repo}}',
                          on_create_set_props={'svn:ignore': 'projects.txt\n'},
                          create_if_necessary=True),
        tasks.FetchRequirements('check out requirements/', '{{config.requirements_svn_repo}}',
                                'requirements'),
        EnvironRefresh(),
        tasks.SaveSetting('Save var setting',
                          {'var': '{{os.path.abspath(config.var)}}'}),
        tasks.SaveSetting('Save settings',
                          {'base_port': '{{config.base_port}}',
                           'topp_secret_filename': '{{env.var}}/secret.txt',
                           'admin_info_filename': '{{env.var}}/admin.txt',
                           'find_links': '{{config.find_links}}',
                           'db_prefix': '{{config.db_prefix}}',
                           'requirements_svn_repo': '{{config.requirements_svn_repo}}',
                           'projtxt': '{{config.projtxt}}',
                           'projprefs': '{{config.projprefs}}',
                           'etc_svn_subdir': '{{config.etc_svn_subdir}}',
                           'localbuild': '{{config.localbuild}}',
                           'num_extra_zopes': '{{config.num_extra_zopes}}',
                           },
                          overwrite=True,
                          validators={
                'db_prefix': validate_db_prefix,
                'num_extra_zopes': validate_num_extra_zopes
                },
                          ),
        tasks.SaveSetting(
            'Save google maps API key settings',
            {'openplans.org': 'ABQIAAAAPg0JzaavflEP5HFbvAW11BTB3-H4wTAao1hskyzZKyTqTR1AJRQIyIkPAwUg3Qm5pFsqk78fbsrjDQ',
             'localhost': 'ABQIAAAACgq_R1LiJejH1-2eRRyQvBTwM0brOpm-All5BF6PoaKBxRWWERRkYcknpt7YAYi-YjtUb5J69-e2Hg',
             'nohost': 'bogus_key_used_for_tests',
             'dev.nycstreets.org': 'ABQIAAAACgq_R1LiJejH1-2eRRyQvBQ42FaFWNur_4XCSEHkUOZhqT-5LhT80_6nqiuC2nvOrzbvOLN0PC7grg',
             'dev.yourstreets.org': 'ABQIAAAACgq_R1LiJejH1-2eRRyQvBQbz6J6EYtXVUBa7BucdbOEH1SrphRUT2-E4Pe2M5U4iDeS9qzQXHoT1A',
             },
             section='google_maps_keys', overwrite=False),
        
        tasks.EnsureDir('Make sure var directory exists', '{{env.var}}', svn_add=False),
        tasks.EnsureFile('Write OpenCore shared secret to var/secret.txt if it does not exist',
                         '{{env.var}}/secret.txt',
                         '{{env.random_string(40)}}',
                         overwrite=False),
        EnsureAdminFile('Write Zope administrator login to var/admin.txt if it does not exist'),
        tasks.VirtualEnv(path='fassembler', never_create_virtualenv=True),
        tasks.InstallSpecIfPresent('Install Fassembler add-on packages',
                                   '{{config.spec}}'),
        ]



class SupervisorProject(Project):
    """
    Sets up Supervisor2 (http://www.plope.com/software/supervisor2/)
    """
    name = 'supervisor'
    title = 'Install Supervisor2'
    project_base_dir = os.path.join(os.path.dirname(__file__), 'supervisor-files')

    settings = [
        Setting('spec',
                default='requirements/supervisor-req.txt',
                help='Specification for installing Supervisor'),
        Setting('port',
                default='{{env.base_port+int(config.port_offset)}}',
                help="Port to install HTTP server on"),
        Setting('port_offset',
                default='10',
                help='Offset from base_port for HTTP server'),
        Setting('supervisor_var',
                default='{{env.var}}/supervisor',
                help="The path to use for supervisor's socket and pidfile; "
                "if you are building an instance in parallel to a running site "
                "you may want to point this elsewhere from env.var so that "
                "you can run both supervisor processes simultaneously"),
        ]
    
    actions = [
        tasks.VirtualEnv(),
        tasks.InstallSpec('Install Supervisor',
                          '{{config.spec}}'),
        tasks.CopyDir('Create config layout', project_base_dir, './'),
        tasks.EnsureDir('Ensure log directory exists',
                        '{{env.var}}/logs/supervisor'),
        tasks.EnsureDir('Ensure pid location exists',
                        '{{config.supervisor_var}}'),
        ]
