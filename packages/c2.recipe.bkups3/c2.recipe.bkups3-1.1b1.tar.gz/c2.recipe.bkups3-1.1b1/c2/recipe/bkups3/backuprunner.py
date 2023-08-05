#!/usr/bin/env python
# encoding: utf-8
"""
backuprunner.py

Created by Manabu Terada on 2011-04-13.
Copyright (c) 2011 CMScom. All rights reserved.
"""

import sys
import os
import tarfile
import hashlib
import shutil
import shelve
from DateTime import DateTime
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import logging

logger = logging.getLogger('bkups3')

S3_FILES_FOLDER = 'files'
S3_BLOBS_FOLDER = 'blobs'
S3_BLOBS_FILENAME = 'blobs.tar.gz'
BLOB_ARCHIVE = "blobs.tar.gz"
BLOB_FILES_DIGEST = "blob_files_digest"


def get_file_md5(filename):
    m = hashlib.md5()
    with open(filename, 'rb') as f:
        m.update(f.read())
    digest = m.hexdigest()
    return digest

def quote_command(command):
    # Quote the program name, so it works even if it contains spaces
    command = " ".join(['"%s"' % x for x in command])
    if sys.platform[:3].lower() == 'win':
        # odd, but true: the windows cmd processor can't handle more than
        # one quoted item per string unless you add quotes around the
        # whole line.
        command = '"%s"' % command
    return command


def make_tar(folder_path, tar_name):
     arcname = os.path.basename(folder_path)
     out = tarfile.TarFile.open(tar_name, 'w:gz')
     out.add(folder_path, arcname)
     out.close()
     return tar_name

def get_blob_files_digest(path):
    dic = {}
    for p, subdirs, files in os.walk(path):
        for d in subdirs:
            pass
        for f in files:
            digest = get_file_md5(os.path.join(p, f))
            dic[os.path.join(p, f)] = digest
    return dic

def chk_digest(new, old_db):
    d = dict((k, v) for k, v in old_db.items())
    if new == d:
        return False
    else:
        return True

def _get_file_time(dirname, filename):
    return DateTime(os.path.getmtime(os.path.join(dirname,filename)))


def send_s3(aws_id, aws_key, bucket_name, bucket_sub_folder, sync_s3_filesfolder, 
                backup_location, 
                blob_bk_filename, use_blobstorage, need_blob_send):
    """Sendding to S3 for backup & blob backup file, and sync to backup filen on S3.
    """
    send_files = []
    conn = S3Connection(aws_id, aws_key)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)

    # files
    files_folder = '/'.join(f for f in (bucket_sub_folder, S3_FILES_FOLDER,) if f)
    rs = dict((key.name, key.last_modified) for key in bucket.list(files_folder))
    files = os.listdir(backup_location)
    for filename in files:
        if filename.startswith('.'):
            continue
        full_filename = '/'.join((files_folder, filename))
        if full_filename in rs:
            if _get_file_time(backup_location, filename) > DateTime(rs[full_filename]):
                f = os.path.join(backup_location, filename)
                k.key = full_filename
                k.set_contents_from_filename(f)
                send_files.append(k.key)
        else:
            f = os.path.join(backup_location, filename)
            k.key = '/'.join((files_folder, filename))
            k.set_contents_from_filename(f)
            send_files.append(k.key)
    
    # Remove rs in filename
    if sync_s3_filesfolder:
        full_filenames = ['/'.join((files_folder, filename)) for filename in files]
        for s3_filename, s3_filedate in rs.items():
            if s3_filename not in full_filenames:
                bucket.delete_key(s3_filename)

    # blobs
    if use_blobstorage and need_blob_send:
        now_date = DateTime().strftime('%Y%m%d%H%M')
        k.key = '/'.join(f for f in (bucket_sub_folder, S3_BLOBS_FOLDER, 
                            now_date, S3_BLOBS_FILENAME) if f)
        k.set_contents_from_filename(blob_bk_filename)
        send_files.append(k.key)

def _comp_func_folder_date(l):
    return DateTime(l[1])

def remove_s3_blobs(aws_id, aws_key, bucket_name, bucket_sub_folder, blob_store_count):
    """Remove blob files on S3 at old blob backup files.
    """
    conn = S3Connection(aws_id, aws_key)
    bucket = conn.get_bucket(bucket_name)
    k = Key(bucket)
    files_folder = '/'.join(f for f in (bucket_sub_folder, S3_BLOBS_FOLDER,) if f)
    list_folders = list(bucket.list(files_folder))
    diff_len = len(list_folders) - blob_store_count
    if diff_len > 0:
        sorted_folders = sorted([(key.name, key.last_modified) for key in list_folders],
                    key=_comp_func_folder_date)
        for name, date in sorted_folders[:diff_len]:
            bucket.delete_key(name)


def _get_files_for_send(backup_location):
    now = DateTime()
    yesterday = now - 1
    files = os.listdir(backup_location)
    for filename in files:
        if filename.startswith('.'):
            continue
        if _get_file_time(backup_location, filename) > yesterday:
            yield filename

def _get_blobfiles_for_send(blob_bk_base_filename):
    now_date = DateTime().strftime('%Y%m%d%H%M')
    return now_date + '.' + blob_bk_base_filename

def _scp_command(location, src_filename, scp_user, scp_server, scp_path, 
                                dst_filename=None):
    kws = {'filename' : src_filename, 
            'scp_user' : scp_user,
            'scp_server' : scp_server,
            'scp_path' : scp_path,
            'fullpath_filename' : os.path.join(location, src_filename)}
    if dst_filename is None:
        kws['dst_filename'] = src_filename
    else:
        kws['dst_filename'] = dst_filename
    os.system(quote_command(['scp', kws['fullpath_filename'], 
                "%(scp_user)s@%(scp_server)s://%(scp_path)s/%(dst_filename)s" % kws]))

def _cp_command(location, src_filename, copy_path, dst_filename=None):
    src = os.path.join(location, src_filename)
    if dst_filename is None:
        dst_filename = src_filename
    dst = os.path.join(copy_path, dst_filename)
    shutil.copyfile(src, dst)

def send_scp(backup_location, scp_user, scp_server, scp_path, 
            blob_bk_location, blob_bk_filename, use_blobstorage, need_blob_send):
    """Sendding by SCP but cannot remove to file on sennding server. 
    """
    files = _get_files_for_send(backup_location)
    for filename in files:
        _scp_command(backup_location, filename, scp_user, scp_server, scp_path)

    if use_blobstorage and need_blob_send:
        blob_bk_base_filename = os.path.basename(blob_bk_filename)
        blob_file = _get_blobfiles_for_send(blob_bk_base_filename)
        _scp_command(blob_bk_location, blob_bk_base_filename, scp_user, scp_server,
                             scp_path, blob_file)
    return None

def send_other_folder(backup_location, copy_path, blob_bk_location, 
                    blob_bk_filename, use_blobstorage, need_blob_send):
    """Sendding to other folder on local server, but cannot remove to file 
    on other folder yet.
    """
    files = _get_files_for_send(backup_location)
    for filename in files:
        _cp_command(backup_location, filename, copy_path)

    if use_blobstorage and need_blob_send:
        blob_bk_base_filename = os.path.basename(blob_bk_filename)
        blob_file = _get_blobfiles_for_send(blob_bk_base_filename)
        _cp_command(blob_bk_location, blob_bk_base_filename, copy_path, blob_file)
    return None



def backup_main(bin_dir, blobstorage_path, backup_location, blob_bk_location, 
                use_s3, aws_id, aws_key, bucket_name, bucket_sub_folder, 
                sync_s3_filesfolder, blob_store_count, use_blobstorage,
                use_scp, scp_user, scp_server, scp_path, use_copy_to_other_folder, 
                copy_path):
    """Main method, gets called by generated bin/bkups3.
    """
    # Data.fs backup , using collective.recipe.backup
    backup = os.path.join(bin_dir, 'backup')
    os.system(quote_command([backup]))
    
    # blobs
    if use_blobstorage:
        new_digest = get_blob_files_digest(blobstorage_path)
        old_digest_db = shelve.open(os.path.join(blob_bk_location, BLOB_FILES_DIGEST))
        if chk_digest(new_digest, old_digest_db):
            old_digest_db.clear()
            old_digest_db.update(new_digest)
            old_digest_db.close()
            
            blob_bk_filename = make_tar(blobstorage_path, 
                                os.path.join(blob_bk_location, BLOB_ARCHIVE))
            logger.info("Backing up blobstorage files: %s .",
                        blob_bk_filename)
            need_blob_send = True
        else:
            old_digest_db.close()
            blob_bk_filename = ""
            need_blob_send = False
    else:
        blob_bk_filename = ""
        need_blob_send = False

    # To S3
    if use_s3:
        stror_files = send_s3(aws_id, aws_key, bucket_name, bucket_sub_folder, 
                            sync_s3_filesfolder, backup_location, blob_bk_filename, 
                            use_blobstorage, need_blob_send)
        logger.info("Sending S3 : %s .",
                    stror_files)
        # Remuve over blob_store_count
        if use_blobstorage:
            remove_files = remove_s3_blobs(aws_id, aws_key, bucket_name, bucket_sub_folder,
                                        blob_store_count)
            logger.info("Remove S3 : %s .",
                        remove_files)

    # To SCP
    if use_scp:
        send_scp(backup_location, scp_user, scp_server, scp_path, 
                    blob_bk_location, blob_bk_filename,
                    use_blobstorage, need_blob_send)
    
    # To other folder
    if use_copy_to_other_folder:
        send_other_folder(backup_location, copy_path, blob_bk_location,
                     blob_bk_filename, use_blobstorage, need_blob_send)

if __name__ == '__main__':
    backup_main()

