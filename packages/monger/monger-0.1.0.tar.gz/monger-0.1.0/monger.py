# -*- coding: utf-8 -*-
''' monger
basic static backups with mongodump
'''
import datetime
import os

import boto
from boto.s3.key import Key
import envoy

class Monger():
    ''' sending mongodump outputs to S3
    '''
    def __init__(self, config_path, working_directory):
        # the dump file will briefly exist here
        self.working_directory = working_directory
        # load the config into the builtins
        # pattern copied from flask's config loading methods
        builtins = {}
        try:
            execfile(config_path, builtins)
        except IOError, e:
            e.strerror = 'Unable to load config file (%s)' % e.strerror
            raise
        self.credentials = builtins['AWS']

    def dump(self):
        ''' runs mongodump
        outputs to a specific dir
        '''
        dump_directory = os.path.join(self.working_directory, 'dump/')
        envoy.run('mongodump -o %s' % dump_directory)

    def create_archive(self):
        ''' creates tarball
        '''
        dump_directory = os.path.join(self.working_directory, 'dump/')
        self.archive_directory = os.path.join(self.working_directory
                , 'dump.tgz')
        envoy.run('tar -czf %s %s' % (self.archive_directory, dump_directory))

    def upload(self, bucket_name):
        connection = boto.connect_s3(
                aws_access_key_id=self.credentials['access_key_id']
                , aws_secret_access_key=self.credentials['secret_access_key'])

        # buckets must be globally unique
        # appending the access_key_id is good for enforcing a namespace
        bucket_name = '%s-%s' % (bucket_name
                , self.credentials['access_key_id'])
        # create the bucket if it doesn't already exist
        bucket = connection.create_bucket(bucket_name.lower())

        s3_key = Key(bucket)
        # ISO 8601 naming
        s3_key.key = datetime.datetime.utcnow().strftime(
                '%Y-%m-%dT%H:%M:%SZ.tgz')
        s3_key.set_contents_from_filename(self.archive_directory)
