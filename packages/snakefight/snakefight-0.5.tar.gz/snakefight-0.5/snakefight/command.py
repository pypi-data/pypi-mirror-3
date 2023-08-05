"""setuptools/distutils `bdist_war` command"""
from __future__ import with_statement
import glob
import os
import shutil
import sys
import tempfile
import zipfile
from StringIO import StringIO
from distutils import log
from distutils.dir_util import mkpath, remove_tree
from distutils.errors import DistutilsError, DistutilsOptionError
from distutils.sysconfig import get_python_version

from pkg_resources import working_set
from setuptools import Command

from snakefight.util import gen_paste_loadapp, gen_web_xml

is_jython = sys.platform.startswith('java')

class bdist_war(Command):

    """Create a WAR file from a Jython WSGI application"""

    description = __doc__

    user_options = [
        ('web-xml=', None, 'Path to the web.xml file'),
        ('war-prefix=', None,
         "Prefix of the war file to build (defaults to distribution's "
         'egg name)'),
        ('jython-home=', None,
         'JYTHON_HOME (defaults to the current home when ran under jython)'),
        ('no-jython', None, "Don't include the Jython distribution"),
        ('include-jars=', None,
         'List of jar files to include in WEB-INF/lib (space or '
         'comma-separated)'),
        ('paste-config=', None,
         'paste.app_factory config file. Automatically generates a web.xml '
         'when specified'),
        ('paste-app-name=', None,
         'paste.app_factory named application (defaults to main)'),
        ]

    boolean_options = ['no-jython']

    def initialize_options (self):
        # command line options
        self.web_xml = None
        self.war_prefix = None
        # support virtualenvs by checking real_prefix first
        self.jython_home = (getattr(sys, 'real_prefix', sys.prefix) if is_jython
                            else None)
        self.no_jython = False
        self.include_jars = None
        self.paste_config = None
        self.paste_app_name = 'main'

        self.war = None

    def finalize_options(self):
        if not self.no_jython and not is_jython and not self.jython_home:
            raise DistutilsOptionError(
                "Not running under Jython and no 'jython-home' specified")

        if not self.web_xml and not self.paste_config:
            raise DistutilsOptionError('No web.xml specified')

        self.ensure_string_list('include_jars')
        if self.include_jars:
            missing = [jar for jar in self.include_jars
                       if not os.path.exists(jar)]
            if missing:
                raise DistutilsOptionError('include-java-libs do not exist: %s'
                                           % missing)

        # ensure the egg-info metadata
        self.egg_info = self.get_finalized_command('egg_info')
        self.dist_name = self.distribution.get_fullname()
        if is_jython:
            self.dist_name += '-py%s' % get_python_version()

        # setup paths
        bdist = self.get_finalized_command('bdist')
        skel_dir = os.path.join(bdist.bdist_base, 'war')

        self.web_inf = os.path.join(skel_dir, 'WEB-INF' + os.sep)
        self.lib_python = os.path.join(self.web_inf, 'lib-python' + os.sep)

        if self.war_prefix is None:
            self.war_prefix = self.dist_name

        # the final .war location
        self.war_name = os.path.join(bdist.dist_dir, self.war_prefix + '.war')

        # the temp .war location we'll build to
        self.temp_war = os.path.join(skel_dir, os.path.basename(self.war_name))

    def run(self):
        self.setup()
        try:
            self._run()
        finally:
            self.teardown()

    def _run(self):
        mkpath(os.path.dirname(self.web_inf), dry_run=self.dry_run)

        if not self.dry_run:
            self.war = zipfile.ZipFile(self.temp_war, 'w')

        if os.path.exists(self.lib_python):
            remove_tree(self.lib_python, dry_run=self.dry_run)
        mkpath(os.path.dirname(self.lib_python), dry_run=self.dry_run)

        self.add_eggs()
        self.add_jars()
        if not self.no_jython:
            self.add_jython()
        self.add_web_xml()

        mkpath(os.path.dirname(self.war_name), dry_run=self.dry_run)
        if not self.dry_run:
            self.war.close()
            shutil.move(self.temp_war, self.war_name)
        log.info('created %s' % self.war_name)

    def setup(self):
        # setup paths for the easy_install command
        sys.path.insert(0, self.egg_info.egg_base)
        working_set.add_entry(self.egg_info.egg_base)

        os.putenv('PYTHONPATH', os.path.abspath(self.lib_python))
        os.environ['PYTHONPATH'] = os.path.abspath(self.lib_python)

        log.set_verbosity(self.verbose)

    def teardown(self):
        os.unsetenv('PYTHONPATH')
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']
        if self.war:
            self.war.close()

    def write(self, arcpath, filename):
        arcname = os.path.join(arcpath, os.path.basename(filename))
        log.debug('adding %s' % arcname)
        if not self.dry_run:
            self.war.write(filename, arcname)

    def writestr(self, arcname, bytes):
        # Generate a temp file because ZipInfo.writestr defaults to lame
        # permissions
        log.debug('adding %s' % arcname)
        if not self.dry_run:
            temp = tempfile.NamedTemporaryFile()
            temp.write(bytes)
            temp.flush()
            self.war.write(temp.name, arcname)

    def add_eggs(self):
        # XXX: sitepy_installed is hacky, it's to avoid overwriting our
        # site.py
        ei_kwargs = dict(args=['.', 'setuptools'], zip_ok=False,
                         install_dir=self.lib_python, exclude_scripts=True,
                         always_copy=True, local_snapshots_ok=True,
                         sitepy_installed=True, verbose=0)
        self.reinitialize_command('easy_install', **ei_kwargs)

        log.info('running easy_install %s' % self.egg_info.egg_name)
        if self.verbose < 2:
            # Hide easy_install warnings
            sys.stdout = sys.stderr = StringIO()
        try:
            if not self.dry_run:
                # XXX: setuptools dry_run=1 fails
                self.run_command('easy_install')
        finally:
            if self.verbose < 2:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

        log.info('adding eggs (to WEB-INF/lib-python)')
        self.write_libs(self.lib_python)

    def write_libs(self, path):
        path = os.path.normpath(path)
        for root, dirs, files in os.walk(path):
            for file in files:
                arcpath = os.path.join('WEB-INF/lib-python',
                                       root[len(path) + 1:], file)
                log.debug('adding %s' % arcpath)
                if not self.dry_run:
                    self.war.write(os.path.join(root, file), arcpath)

    def add_jython(self):
        # XXX: Add check for jython_home being a jar, then just copy the
        # jar (standalone, no Lib/ copying needed)
        jython_complete = os.path.join(self.jython_home, 'jython.jar')
        jython = os.path.join(self.jython_home, 'jython-dev.jar')
        if os.path.exists(jython_complete):
            log.info('adding WEB-INF/lib/%s' %
                     os.path.basename(jython_complete))
            self.write('WEB-INF/lib', jython_complete)
            self.write_libs(os.path.join(self.jython_home, 'Lib'))
        elif os.path.exists(jython):
            log.info('adding WEB-INF/lib/%s and its jars/libs' %
                     os.path.basename(jython))
            self.write('WEB-INF/lib', jython)
            for path in glob.iglob(os.path.join(self.jython_home, 'javalib',
                                                '*.jar')):
                self.write('WEB-INF/lib', path)
            self.write_libs(os.path.join(self.jython_home, 'Lib'))
        else:
            raise DistutilsError('Could not find Jython distribution')

    def add_jars(self):
        if not self.include_jars:
            return
        log.info('adding jars (to WEB-INF/lib)')
        for jar in self.include_jars:
            self.write('WEB-INF/lib', jar)

    def add_web_xml(self):
        if not self.web_xml:
            # Paste app: generate a web.xml and an apploader
            app_import_name = self.add_paste_loadapp(self.paste_config,
                                                     self.paste_app_name)
            log.info('generating deployment descriptor')
            web_xml = gen_web_xml(
                display_name=self.distribution.get_name(),
                description=self.distribution.get_description(),
                app_import_name=app_import_name)
        else:
            with open(self.web_xml) as fp:
                web_xml = fp.read()

        filename = 'WEB-INF/web.xml'
        log.info('adding deployment descriptor (%s)' % filename)
        self.writestr(filename, web_xml)

    def add_paste_loadapp(self, config, app_name):
        log.info('adding Paste ini file (to %s)' % os.path.basename(config))
        self.write('WEB-INF', self.paste_config)

        filename = 'WEB-INF/lib-python/____loadapp.py'
        log.info('adding Paste app loader (to %s)' % filename)
        self.writestr(filename, gen_paste_loadapp(config, app_name))
        return '____loadapp.loadapp()'
