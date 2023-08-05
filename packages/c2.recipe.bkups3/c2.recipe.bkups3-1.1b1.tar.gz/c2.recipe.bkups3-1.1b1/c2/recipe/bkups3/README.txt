Supported options
=================

The recipe supports the following options:

blob_bk_dir_name
    setting backup path name. 
    defalut: blobbackups

use_s3
    default: false
    Using S3 is true, Not use S3 is false

aws_id
	<aws access key>
	
aws_key
	<aws secret key>

bucket_name
	<S3 bucket name>
	setting unique bucket name in Amazon S3

bucket_sub_folder
    Option: Sub folder in S3 bucket

sync_s3_filesfolder
    default: true

blob_store_count
    defalut : 1
	Saved number of blob files

use_scp
    default: false
    Using scp is true, Not use scp is false
    New attribute from ver 1.1

scp_user
    <SCP username>
    Need to put ssh key
    New attribute from ver 1.1

scp_server
    <SCP ServerName>
    Server name or IP Address
    New attribute from ver 1.1

scp_path
    <SCP URL>
    e.g.: /path/to/folder
    New attribute from ver 1.1

use_copy_to_other_folder
    default: false
    Using copy to other folder is true, Not use copy is false
    New attribute from ver 1.1

copy_path
    <folder path>
    Need to create the folder
    e.g.: /var/backup/folder
    New attribute from ver 1.1

We'll use all options::

	>>> write('buildout.cfg',
	... """
	... [buildout]
	... parts = bkups3
	...
	... [bkups3]
	... recipe = c2.recipe.bkups3
	... blob_bk_dir_name = blobbackups
	... use_s3 = true # Using S3 -- true, Not use S3 -- false
	... aws_id = xxxxxxxxxxxx
	... aws_key = xxxxxxxxxxxxxxxxxxxxxxxxx
	... bucket_name = xxxxxxxx
	... bucket_sub_folder = mysitename
	... sync_s3_filesfolder = true
	... blob_store_count = 7 # Stored 7 times
    ... use_scp = true
    ... scp_user = User_name
    ... scp_server = Your.domain.name
    ... scp_path = /path/to/folder
    ... use_copy_to_other_folder = true
    ... copy_path = /var/backup/folder
	... """)
    >>> print system(buildout) # doctest:+ELLIPSIS
    Installing backuptos3.
    backup: Created /sample-buildout/var/backups/blobstorage
    Generated script '/sample-buildout/bin/bkups3'.


Example usage
=============

Just to isolate some test differences, we run an empty buildout once::

    >>> ignore = system(buildout)

We'll start by creating a buildout that uses the recipe::

	>>> write('buildout.cfg',
	... """
	... [buildout]
	... parts = bkups3
	...
	... [bkups3]
	... recipe = c2.recipe.bkups3
	... use_s3 = true
	... """)

Running the buildout adds a bkups3 scripts to the
``bin/`` directory and, by default, it creates the ``var/bkups3`` dirs::

    >>> print system(buildout) # doctest:+ELLIPSIS
    Installing backuptos3.
    backup: Created /sample-buildout/var/backups/blobstorage
    Generated script '/sample-buildout/bin/bkups3'.
    <BLANKLINE>
    >>> ls('var')
    d  blobbackups
    >>> ls('bin')
    -  bkups3
    -  buildout



Backup
=============

Calling ``bin/bkups3`` results in a normal repozo backup and blobstorage backup and store to Amazon S3. We put in place a
mock repozo script that prints the options it is passed (and make it
executable). It is horridly unix-specific at the moment.

    >>> import sys
    >>> write('bin', 'repozo',
    ...       "#!%s\nimport sys\nprint ' '.join(sys.argv[1:])" % sys.executable)
    >>> #write('bin', 'repozo', "#!/bin/sh\necho $*")
    >>> dontcare = system('chmod u+x bin/repozo')

    >>> import sys
    >>> write('bin', 'backup',
    ...       "#!%s\nimport sys\nprint ' '.join(sys.argv[1:])" % sys.executable)
    >>> #write('bin', 'backup', "#!/bin/sh\necho $*")
    >>> dontcare = system('chmod u+x bin/backup')

By default, backups are done in ``var/backuptos3``::

    >>> print system('bin/bkups3')
    --backup -f /sample-buildout/var/filestorage/Data.fs -r /sample-buildout/var/backups --gzip
    INFO: Backing up database file: ...


	