# -*- coding: utf-8 -*-
"""Recipe bkups3"""

import os
import zc.buildout
import logging

logger = logging.getLogger('bkups3')

class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        if 'collective.recipe.backup' not in self.buildout['versions']:
            logger.error("Can't find collective backup recipe in eggs")
            raise zc.buildout.UserError("Can't find backup recipe in eggs")
        if 'plone.app.blob' in self.buildout['versions']:
            self.use_blobstorage = True
        else:
            self.use_blobstorage = False
        bin_dir = self.buildout['buildout']['bin-directory']
        buildout_dir = os.path.join(bin_dir, os.path.pardir)
        backup_dir = self.buildout['backup']['location']
        blob_bk_dir_name = self.options.get('blob_bk_dir_name', 'blobbackups')
        blob_bk_dir = os.path.join(buildout_dir, 'var', blob_bk_dir_name)
        
        options.setdefault('buildout_dir', buildout_dir)
        options.setdefault('backup_dir', backup_dir)
        options.setdefault('blob_bk_dir', blob_bk_dir)
        options.setdefault('use_s3', 'false')
        options.setdefault('aws_id', '')
        options.setdefault('aws_key', '')
        options.setdefault('bucket_name', '')
        options.setdefault('bucket_sub_folder', '')
        options.setdefault('sync_s3_filesfolder', 'ture')
        options.setdefault('blob_store_count', '1')
        self.egg = zc.recipe.egg.Egg(buildout, options['recipe'], options)
        
        python = buildout['buildout']['python']
        options['executable'] = buildout[python]['executable']
        options['bin-directory'] = buildout['buildout']['bin-directory']
        options['blobstorage_path'] = buildout['instance'].get('blob-storage', '')
        options['use_blobstorage'] = str(self.use_blobstorage)
        options['backup_name'] = self.name
        
        check_for_true(options, ['use_s3', 'sync_s3_filesfolder'])
        self.options = options

    def install(self):
        """Installer"""
        # XXX Implement recipe functionality here
        
        # Return files that were created by the recipe. The buildout
        # will remove all returned files upon reinstall.
        buildout_dir = self.options['buildout_dir']
        backup_location = construct_path(
            buildout_dir, self.options['backup_dir'])
        if self.use_blobstorage:
            blob_bk_location = construct_path(
                buildout_dir, self.options['blob_bk_dir'])
        #
        # if not os.path.isdir(backup_location):
        #     os.makedirs(backup_location)
        #     logger.info('Created %s', backup_location)
        if self.use_blobstorage and not os.path.isdir(blob_bk_location):
            os.makedirs(blob_bk_location)
            logger.info('Created %s', blob_bk_location)
        
        
        #
        initialization_template = """
import logging
loglevel = logging.INFO
# Allow the user to make the script more quiet (say in a cronjob):
# if sys.argv[-1] in ('-q', '--quiet'):
#     loglevel = logging.WARN
# logging.basicConfig(level=loglevel,
#     format='%%(levelname)s: %%(message)s')
bin_dir = %(bin-directory)r
blobstorage_path = %(blobstorage_path)r
backup_location = %(backup_location)r
blob_bk_location = %(blob_bk_location)r
use_s3 = %(use_s3)s
aws_id = %(aws_id)r
aws_key = %(aws_key)r
bucket_name = %(bucket_name)r
bucket_sub_folder = %(bucket_sub_folder)r
sync_s3_filesfolder = %(sync_s3_filesfolder)s
blob_store_count = %(blob_store_count)s
use_blobstorage = %(use_blobstorage)s
"""
        opts = self.options.copy()
        opts['backup_location'] = backup_location
        opts['blob_bk_location'] = blob_bk_location
        initialization = initialization_template % opts
        requirements, ws = self.egg.working_set(['c2.recipe.bkups3',
                                                 'zc.buildout',
                                                 'zc.recipe.egg'])
        
        scripts = zc.buildout.easy_install.scripts(
            [(self.options['backup_name'],
              'c2.recipe.bkups3.backuprunner',
              'backup_main')],
            #requirements,
            ws, self.options['executable'], self.options['bin-directory'],
            arguments=('bin_dir, blobstorage_path, backup_location,'+
                            'blob_bk_location, use_s3, aws_id, aws_key, bucket_name, '+
                            'bucket_sub_folder, sync_s3_filesfolder, blob_store_count, '+
                            'use_blobstorage'),
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