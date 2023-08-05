# -*- coding: utf-8 -*-
"""Recipe bitbucketbk"""

import os
import zc.buildout
import zc.recipe.egg
import logging

logger = logging.getLogger('bitbucketbk')

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        bin_dir = self.buildout['buildout']['bin-directory']
        buildout_dir = os.path.join(bin_dir, os.path.pardir)
        options.setdefault('buildout_dir', buildout_dir)
                
        options.setdefault('username', '')
        options.setdefault('password', '')
        options.setdefault('location', 'backups')
        ignore_project = options.get('ignore_project', '')
        self.ignore_projcet = tuple([ignore.strip() for ignore in
                                        ignore_project.split('\n') if ignore.strip()])
        
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['backup_name'] = self.name
        check_for_true(options, [])
        
        self.options = options

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        buildout_dir = self.options['buildout_dir']
        backup_location = construct_path(
            buildout_dir, self.options['location'])

        if not os.path.isdir(backup_location):
            os.makedirs(backup_location)
            logger.info('Created %s', backup_location)

        #
        initialization_template = """
import logging
loglevel = logging.INFO
# Allow the user to make the script more quiet (say in a cronjob):
# if sys.argv[-1] in ('-q', '--quiet'):
#     loglevel = logging.WARN
# logging.basicConfig(level=loglevel,
#     format='%%(levelname)s: %%(message)s')
username = %(username)r
password = %(password)r
location = %(location)r
ignore_project = %(ignore_project)r
"""
        opts = self.options.copy()
        opts['ignore_project'] = self.ignore_projcet
        initialization = initialization_template % opts
        requirements, ws = self.egg.working_set(['c2.recipe.bitbucketbk',
                                                 'zc.buildout',
                                                 'zc.recipe.egg'])
        
        scripts = zc.buildout.easy_install.scripts(
            [(self.options['backup_name'],
              'c2.recipe.bitbucketbk.backuprunner',
              'backup_main')],
            #requirements,
            ws, self.options['executable'], self.options['bin-directory'],
            arguments=('username, password, location, ignore_project'),
            initialization=initialization)
        return scripts


    def update(self):
        """Updater"""
        pass


def check_for_true(options, keys):
    """Set the truth options right.

    Default value is False, set it to True only if we're passed the string
    'true' or 'True'. Unify on a capitalized True/False string.

    """
    for key in keys:
        if options[key].lower() == 'true':
            options[key] = 'True'
        else:
            options[key] = 'False'

def construct_path(buildout_dir, path):
    """Return absolute path, taking into account buildout dir and ~ expansion.

    Normal paths are relative to the buildout dir::

      >>> buildout_dir = '/somewhere/buildout'
      >>> construct_path(buildout_dir, 'var/filestorage/Data.fs')
      '/somewhere/buildout/var/filestorage/Data.fs'

    Absolute paths also work::

      >>> construct_path(buildout_dir, '/var/filestorage/Data.fs')
      '/var/filestorage/Data.fs'

    And a tilde, too::

      >>> userdir = os.path.expanduser('~')
      >>> desired = userdir + '/var/filestorage/Data.fs'
      >>> result = construct_path(buildout_dir, '~/var/filestorage/Data.fs')
      >>> result == desired
      True

    Relative links are nicely normalized::

      >>> construct_path(buildout_dir, '../var/filestorage/Data.fs')
      '/somewhere/var/filestorage/Data.fs'

    Also $HOME-style environment variables are expanded::

      >>> import os
      >>> os.environ['BACKUPDIR'] = '/var/backups'
      >>> construct_path(buildout_dir, '$BACKUPDIR/myproject')
      '/var/backups/myproject'

    """
    path = os.path.expanduser(path)
    path = os.path.expandvars(path)
    combination = os.path.join(buildout_dir, path)
    normalized = os.path.normpath(combination)
    return normalized