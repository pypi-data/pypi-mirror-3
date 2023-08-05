Requirement
================

- Plone

  - Plone 4.0 (tested by 4.0.4 on MacOS 10.6)
  - Support SSL in Python (If your backup destination is AWS-S3)

- Amazon web service account(If your backup destination is AWS-S3)

  - Amazon web service account (aws access key / aws secret key)
  - S3 root bucket name


Information
================

- Code repository: https://bitbucket.org/cmscom/c2.recipe.bkups3
- Questions and comments to terada@cmscom.jp
- Report bugs at https://bitbucket.org/cmscom/c2.recipe.bkups3/issues
- Referred to http://pypi.python.org/pypi/collective.recipe.backup


Note
=======

If you don't have ``repozo`` command in bin folder, you need to add the lines in `buildout.cfg`.  The following lines will create ``bin/buckup`` script witch this recipe is using.

buildout.cfg ::

    [repozo]
	recipe = zc.recipe.egg
	eggs = ZODB3
	scripts = repozo
	


Simple usage
==============

Modify buildout.cfg ::

    parts = 
       ...
       bkups3

    [bkups3]
    recipe = c2.recipe.bkups3
    use_s3 = true
    aws_id = xxxxxxxxxxxxx
    aws_key = xxxxxxxxxxxxxxxxxxxxxxxxxx
    bucket_name = xxxxxxxxxx
    bucket_sub_folder = mysitename
    sync_s3_filesfolder = true
    blob_store_count = 7

Run the buildout ::

    bin/buildout -N

You can use backup scripts ::

    bin/bkups3

You will see  filestorage backups in  `var/backups` , blobstorage backup in `var/blobbackups` 
and the Amazon Web Service S3 bucket which you sepecified.

