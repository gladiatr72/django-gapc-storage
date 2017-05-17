
import base64
import json
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .storage import GoogleCloudStorage
from oauth2client.client import SERVICE_ACCOUNT
from oauth2client.service_account import ServiceAccountCredentials


class Storage(GoogleCloudStorage):
    """
    Custom subclass of GoogleCloudStorage to facilitate static file handling
    """

    name = 'static'
    path_prefix = getattr(settings, 'STATIC_PREFIX', '')
    bucket = os.environ.get('GCS_STATIC_BUCKET',
                            getattr(settings, 'GCS_STATIC_BUCKET', None)
                            )

    if not bucket:
        raise ImproperlyConfigured(
            "GCS_STATIC_BUCKET (environment variable|django setting) not set"
        )

    def get_oauth_credentials(self):
        try:
            client_credentials = json.loads(base64.b64decode(os.environ["GCS_CREDENTIALS"]))
        except TypeError:
            try:
                client_credentials = json.loads(os.environ["GCS_CREDENTIALS"])
            except KeyError:
                raise KeyError('GCS_CREDENTIALS env variable not set')

        if client_credentials["type"] == SERVICE_ACCOUNT:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(client_credentials)
        else:
            raise ImproperlyConfigured("non-service accounts are not supported")
        return self.create_scoped(creds)
