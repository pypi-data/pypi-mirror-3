import os
import datetime
import mimetypes

from boto.s3.connection import S3Connection, SubdomainCallingFormat, VHostCallingFormat
from boto.s3.key import Key
from django.conf import settings as django_settings
from django.core.files.base import File
from django.core.files.storage import Storage
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import smart_str


try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

settings = getattr(django_settings, 'AWS_S3_SETTINGS', None)
if settings is None:
    raise ImproperlyConfigured("Missing settings for AWS_S3_SETTINGS")

__all__ = ['S3Storage']

class S3Storage(Storage):
    def __init__(self):
        calling_format = VHostCallingFormat() if settings.get('custom_domain', False) else SubdomainCallingFormat()
        self.connection = S3Connection(settings['access_key'], settings['secret_key'], calling_format=calling_format)
        self.bucket = self.connection.get_bucket(settings['bucket'])


    def key(self, key_name, make_missing=False):
        key_name = smart_str(key_name)
        key = self.bucket.get_key(key_name)
        if key is None and make_missing is True:
            key = self.bucket.new_key(key_name)

        return key


    def _open(self, name, mode='rb'):
        return S3StorageFile(name, mode, self.key(name, make_missing=True))


    def _save(self, name, content):
        # determining content type seems more convoluted than it should be.
        content_type = getattr(content, 'content_type', None)
        if content_type is None:
            content_type = mimetypes.guess_type(name)[0]

        key = self.key(name, make_missing=True)
        key.set_metadata('Content-Type', content_type or Key.DefaultContentType)
        key.set_contents_from_file(content, policy='public-read')
        return name


    def delete(self, name):
        # Doing some simple checks here instead of erroring.  I believe deletes should be idempotent.
        key = self.key(name)
        if key is not None:
            key.delete()


    def exists(self, name):
        return (self.key(name) is not None)


    def listdir(self, dir_name=''):
        # this seems to be a cludge that maps the way S3 and Django treat paths
        if dir_name and not dir_name.endswith('/'):
            dir_name += '/'

        listing = self.bucket.list(smart_str(dir_name))

        directories, files = set(), []
        for key in listing:
            key_name = key.name
            # This cleans up the dir_name off of sub listings of since the key system is a fake filesystem
            if dir_name and key_name.startswith(dir_name):
                key_name = key_name[len(dir_name):]
                if not key_name:
                    continue

            # if there are no slashes left we know we're a file
            if key_name.count('/') == 0:
                files.append(key_name)
            else:
                directories.add(key_name.split('/', 1)[0])

        # the casting here should not be, strictly speaking, needed.  But I figured why not.
        return list(directories), files


    def size(self, name):
        return self.key(name).size


    def url(self, name):
        custom_domain = settings.get('custom_domain', False)
        if custom_domain is not False:
            # Forces http since SSL isn't possible on AWS custom domains
            return 'http://{domain}/{path}'.format(domain=custom_domain, path=name)

        return self.connection.generate_url(expires_in=3600, method='GET', bucket=self.bucket.name, key=smart_str(name))


    def accessed_time(self, name):
        # I'm not sure if this is semantically the best call.
        return self.modified_time(name)


    def created_time(self, name):
        # I'm not sure if this is semantically the best call.
        return self.modified_time(name)


    def modified_time(self, name):
        # The timestamp seems to be RFC822 I think, but I'm not 100% sure but this worked in local testing
        last_modified = self.key(name).last_modified
        return datetime.datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z')


    def get_available_name(self, name):
        # This is intentionally stupid at the moment
        return name


class S3StorageFile(File):
    aws_chunk_size = 5 * 1024 ** 2 # 5MB


    def __init__(self, name, mode, key):
        self.name = name
        self.key = key
        self.bucket = key.bucket

        self.upload_session = None
        self.uploaded_chunks = 0

        self.file = StringIO()

        # Mode configuration, a little more convoluted than I hoped, but I think this accurately reflects standard file modes
        self.writable = '+' in mode
        _mode = mode.replace('+', '').replace('b', '').replace('U', '') # strip out characters I don't care about

        if _mode == 'w':
            self.writable = True
        elif _mode == 'a':
            if self.key.exists():
                self.key.get_contents_to_file(self.file)
                self.file.seek(0, os.SEEK_END)
            self.writable = True
        elif _mode == 'r':
            if self.key.exists():
                self.key.get_contents_to_file(self.file)
                self.file.seek(0)
        else:
            raise AttributeError(
                'S3StorageFile \'{name}\' has been attempted to be opened with invalid mode: {mode}'.format(name=name,
                    mode=mode))


    @property
    def size(self):
        return self.key.size


    def current_buffer_content_length(self):
        current_position = self.file.tell()
        self.file.seek(0, os.SEEK_END)
        length = self.file.tell()
        self.file.seek(current_position)
        return length


    def write(self, *args, **kwargs):
        if not self.writable:
            raise AttributeError('{name} was opened for read-only access'.format(name=self.name))

        results = super(S3StorageFile, self).write(*args, **kwargs)

        if self.upload_session is None:
            self.upload_session = self.bucket.initiate_multipart_upload(self.key.name, headers={
                self.bucket.connection.provider.acl_header:'public-read',
                })

        if self.current_buffer_content_length() >= self.aws_chunk_size:
            self.file.seek(0)
            self.upload_session.upload_part_from_file(self.file, self.uploaded_chunks + 1)
            self.uploaded_chunks += 1

            self.file.close()
            self.file = StringIO()

        return results


    def close(self):
        if self.upload_session is not None:
            self.file.seek(0)
            self.upload_session.upload_part_from_file(self.file, self.uploaded_chunks + 1)
            self.upload_session.complete_upload()

        self.file.close()
        self.key.close()

