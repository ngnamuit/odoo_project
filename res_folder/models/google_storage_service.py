from google.cloud import storage
import logging
import os
_logger = logging.getLogger(__name__)

"""ref. https://cloud.google.com/storage/docs/reference/libraries#client-libraries-usage-python"""

path_file = os.path.dirname(__file__) + '/medcodx.json'
print("path_file ===== " + str(path_file))
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = path_file
CLOUD_STORAGE_BUCKET = 'medco_storage' #odoo.tools.config['google_storage_bucket']

def decode_gcs_url(url):
    try:
        import urlparse
    except ImportError:
        import urllib.parse as urlparse
    p = urlparse(url)
    path = p.path[1:].split('/', 1)
    bucket, file_path = path[0], path[1]
    return bucket, file_path

"""
Google API credentials
Different Google services use different credentials
1) Google Maps API requires an API key
2) Google Cloud recommends and prefers using Service Accounts ref. https://cloud.google.com/docs/authentication/
"""
class Storage:
    """
    Resources:
      https://cloud.google.com/apis/docs/cloud-client-libraries
      https://github.com/GoogleCloudPlatform/google-cloud-python/tree/master/storage

    Sample data:
      local_path : './temp/odometer/370f49c3-e1e0-4560-b312-e5be41d8e4fe.jpg'
      filename : 'odometer/f3816404-3308-42e7-8c22-1c7ae0ce065a.jpg'
      blob.public_url : 'https://storage.googleapis.com/aa-storage-staging/odometer%2Ff3816404-3308-42e7-8c22-1c7ae0ce065a.jpg'
    """

    @staticmethod
    def upload(local=None, remote=None, bucket_name=None):
        """
        :local  aka. local path
        :remote aka. remote path

        ref. https://cloud.google.com/storage/docs/uploading-objects#storage-upload-object-python

        sample usage
        remote_filename, remote_url = GoogleApiSvc.Storage.upload(local_path, remote_filename)
        remote_filename, remote_url = GoogleApiSvc.Storage.upload(local_path, remote_filename, bucket_name)

        this will upload local file
        from {local_path}
        to   gs://{AtlasConfig['google'][storage']['bucket]}/{remote_filename}
        to   gs://{bucket_name}                                    /{remote_filename}
        """

        _logger.info(f'[GoogleApi][Storage] ========= Uploading from {local} to {remote}')
        #region validate params
        if not local or not remote:
            _logger.error('[GoogleApi][Storage] Both local and remote paths must be specified.')
            return None, None
        if bucket_name is None: # :bucket_name not available --> use the one set in config
            bucket_name = CLOUD_STORAGE_BUCKET
        #endregion

        storage_client = storage.Client()
        try:
            bucket = storage_client.get_bucket(bucket_name)
            blob = bucket.blob(remote)
            blob.upload_from_filename(local)
            _logger.info(f'[GoogleApi][Storage] Blob ====== Name: {blob.name} was uploaded to public_url: {blob.public_url}')

            # remove local file
            os.remove(local)
            public_url = blob.public_url
            private_url = ''
            if public_url:
                private_url = public_url.replace('storage.googleapis.com', 'storage.cloud.google.com') + '?authuser=0'
            return blob.name, private_url
        except Exception as e:
            _logger.error("[GoogleApi][Storage] Error uploading file: ", e)
            raise


    @staticmethod
    def make_public(blob_name):
        """Makes a blob publicly accessible."""
        storage_client = storage.Client()
        try:
            bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)
            blob = bucket.blob(blob_name)
            blob.make_public()
            _logger.info('[GoogleApi][Storage] Blob {} is publicly accessible at {}'.format(blob.name, blob.public_url))
        except Exception as e:
            _logger.error("[GoogleApi][Storage] Error making file public: ", e)
            raise

    @staticmethod
    def download(public_url, local_path):
        storage_client = storage.Client()
        try:
            bucket, file_path = decode_gcs_url(public_url)
            # bucket = storage_client.get_bucket(CLOUD_STORAGE_BUCKET)
            bucket = storage_client.get_bucket(bucket)
            blob_name = file_path
            if "%2F" in blob_name:
                blob_name = blob_name.replace('%2F', '/')
            blob = bucket.blob(blob_name)
            blob.download_to_filename(local_path + file_path)
            _logger.info(f'[GoogleApi][Storage] Downloaded file to local: {local_path + file_path}')
            return file_path
        except Exception as e:
            _logger.error("[GoogleApi][Storage] Error download file: ", e)
            raise

    def delete_blob(blob_name, bucket_name=None):
        """Deletes a blob from the bucket."""
        # bucket_name = "your-bucket-name"
        # blob_name = "your-object-name"
        if bucket_name is None: # :bucket_name not available --> use the one set in config
            bucket_name = CLOUD_STORAGE_BUCKET
        storage_client = storage.Client()

        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        blob.delete()

        print("Blob {} deleted.".format(blob_name))
