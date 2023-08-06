__version__ = "1.0.1"

import os
import subprocess
import datetime
import tarfile
import hashlib
import logging

from path import path
from boto.s3.connection import S3Connection
from boto.s3.key import Key

from django.conf import settings

log = logging.getLogger('s3backup')


class S3Backup(object):
    backup_dir = path(settings.S3BACKUP_LOCAL_PATH)
    backup_prefix = getattr(settings, 'S3BACKUP_BACKUP_PREFIX', 's3backup_')
    bucket_prefix = path(getattr(settings, 'S3BACKUP_BUCKET_PREFIX', 'backups'))
    dumps = []
    
    def __init__(self):
        """Return a key to store backup on"""
        self.connection = S3Connection(settings.AWS_ACCESS_KEY,
                                        settings.AWS_SECRET_KEY)
        self.bucket = self.connection.get_bucket(settings.AWS_BUCKET)
    
    def dump_postgres(self, dbname):
        """
        Dump a postgres db.
        
        Make sure to set a .pgpass file so no password is needed.
        """
        db = settings.DATABASES[dbname]
        backup_file = '%s%s.sql' % (self.backup_prefix, db['NAME'])
        out = open(self.backup_dir / backup_file, 'w')
        subprocess.check_call(['pg_dump', 
                               db['NAME'],
                               '--user=%s' % db['USER']], stdout=out)
        return out.name
                               
    def dump_databases(self):
        dumps = []
        for dbname in settings.DATABASES:
            if settings.DATABASES[dbname]['ENGINE'] == \
                                    'django.db.backends.postgresql_psycopg2':
                dump = self.dump_postgres(dbname)
                dumps.append(dump)
            else:
                raise NotImplemented('Only postgres dumps implemented yet')
        return dumps

    def compress_dumps(self, dumps):
        """tar.gz compress the local dumps"""
        now = datetime.datetime.now()
        name = self.backup_prefix + now.strftime("%Y-%m-%d_%H:%M:%S.tar.gz")
        tar = tarfile.open(self.backup_dir / name, 'w:gz')
        for dump in dumps:
            tar.add(dump)
        tar.close()
        return path(tar.name)
    
    def get_md5(self, filename, block_size=8192):
        f = open(filename, 'rb')
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()
        
    def get_key(self, filename, prefix):
        name = self.bucket_prefix / prefix / filename
        return Key(self.bucket, name)
        
    def get_local_last_backups_file(self):
        name = self.backup_dir / 'last_backups.txt'
        return open(name, 'w+')

    def get_remote_last_backups(self):
        key = self.bucket.get_key(self.bucket_prefix / 'last_backups.txt')
        
        if not key:
            # no last backups file on server, create some
            key = Key(self.bucket, self.bucket_prefix / 'last_backups.txt')
            key.set_contents_from_string('no_previous_backup;_')

        return key
        
    def store_backup(self, filename, prefix):
        """
        Store a backup file to S3. ``prefix`` will be the last prefix before
        the filename, so you can differentiate daily, weekly montly backups
        etc.
        
        Will not upload the file if it doesn't differ from the latest backup.
        """
        md5 = self.get_md5(filename)
        # last_backup.txt contains a list with the key of the backup, and its
        # md5 separated by a ;. Top one is the last. We always refresh this
        # list from the S3, to make sure we are in sync.
        last_backups_file = self.get_local_last_backups_file()
        last_backups_remote = self.get_remote_last_backups()
        last_backups_remote.get_contents_to_file(last_backups_file)
        last_backups_file.seek(0)
        last_backup = last_backups_file.readline().split(';')

        new_key = self.get_key(filename.name, prefix)
        log.debug('storing backup to %s' % new_key.name)
        if md5 != last_backup[1]:
            new_key.set_contents_from_filename(filename, encrypt_key=True,
                md5=new_key.get_md5_from_hexdigest(md5))
        else:
            last_backup_key = Key(self.bucket, last_backup[0])
            last_backup_key.copy(self.bucket, new_key, encrypt_key=True)
        
        # Update the last_backups.txt
        # As it is only 100 lines long, we can easily load it into memory
        last_backups_file.seek(0)
        lines = last_backups_file.readlines()
        last_backups_file.seek(0)
        last_backups_file.write(';'.join((new_key.name, md5)) + '\n')
        last_backups_file.writelines(lines[:99])
        last_backups_file.close()
        last_backups_remote.set_contents_from_filename(last_backups_file.name)
        
        # Cleanup
        self.cleanup(filename)
        
        return new_key.name
        
    def cleanup(self, filename):
        try:
            os.remove(filename)
        except OSError, e:
            log.warning('Could not cleanup: %s' % e)
    
    def backup(self, prefix='daily'):
        dumps = self.dump_databases()
        compressed = self.compress_dumps(dumps)
        backup_name = self.store_backup(compressed, prefix)
        name = '%s.s3.amazonaws.com/' % self.bucket.name +  backup_name
        return 'Succesfully backupped all databases to %s' % name
        
