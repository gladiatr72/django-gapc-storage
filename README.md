
# (Google Cloud Storage) Storage for Django

## django-gapc-storage

`django-gapc-storage` is a Django storage backend for Google Cloud Storage
using the JSON API through google-api-python-client. This is forked from [django-gapc-storage](https://github.com/eldarion/django-gapc-storage).

------

Eldarion et al.: if you were to stumble upon this repository, please accept my thanks for handling the gooey bits.

------

NOTE: No attempt has been made to create a pull request to the original project because Time.

Enhancements:

* staticfiles support
* properly casts naive dates to conform to Django's expectations


## Requirements

* Django 1.8+
* a GCP service account
* one or two GCS buckets


## Configure a Service Account

From the GCP web console: `IAM & Admin` -> `Service Accounts`, `Create Service Account`, give it a name; finally:  `Create`.

A new account will have no keys. Keys are created, deleted or renamed from the
line menu. `django-gapc-storage` accounts for `json` formatted private key structures.

On key creation, an account specific private key is returned structured thusly (as of 5/30/2017)

```json

{
  "type": "service_account",
  "project_id": "thisn-000000",
  "private_key_id": "3d8a143d635e885350398e5a29385fe0e2f0297f",
  "private_key": "-----BEGIN PRIVATE KEY----- >>[[bits]]<< -----END PRIVATE KEY-----\n",
  "client_email": "throw-away@thisn-000000.iam.gserviceaccount.com",
  "client_id": "000000000000000000000",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/throw-away%40thisn-000000.iam.gserviceaccount.com"
}

```

This library accounts for this JSON string being passed in the GCS_CREDENTIALS environment variable.

*NOTE*: Feeding base64-encoded JSON via this variable will fail. We are currently
targetting Kubernetes for deployments; base64 is automatically decoded when it is encountered as a value within its
secrets store. For local work: ```export GCS_CREDENTIALS="$( cat /path/to/keyfile.json)"```

## Knobs and Switches

 * Django settings only
   * GAPC_STATIC_STORAGE
   * GAPC_MEDIA_STORAGE
   * DEFAULT_FILE_STORAGE
   * STATICFILES_STORAGE
 * Environment or Django settings
   * GCS_STATIC_BUCKET
   * GCS_MEDIA_BUCKET
 * Environment Only
   * GCS_CREDENTIALS



### DEFAULT_FILE_STORAGE

set to the string, `gapc_storage.media.Storage`

### STATICFILES_STORAGE

set to the string, `gapc_storage.static.Storage`

### GAPC_[]_STORAGE

Modify This library's defaults:

```python
GAPC_[]_STORAGE = {
        "allow_overwrite": False,
        "bucket": "my-bucket",
        "cache_control": "public, max-age=3600",
        "num_retries": 0,
        "path_prefix": "",
    }
```

#### allow_overwrite

Default: `False`

If `True`, the storage backend will overwrite an existing object with
the same name.

#### bucket

Default: `os.environ["GCS_[]_BUCKET"]`

#### cache_control

Default: `public, max-age=3600`

By default, public-readable objects on GCS have a cache duration of 60
minutes.  Set `cache_control` to `private, max-age=0` to disable
public caching of objects saved by the storage backend.

#### num_retries

Default: `0`

Passed to the supported methods on the underlying google-api-python-client client which will retry 500 error responses with randomized exponential backoff.

For more information, see the [google-api-python-client documentation](http://google.github.io/google-api-python-client/docs/epy/googleapiclient.http.HttpRequest-class.html#execute)

#### path_prefix

Default: `""`

A prefix appended to the path of objects saved by the storage backend.
For example, configuring path_prefix to `media` would save
objects to `my-bucket/media`.


### GCS_[]_BUCKET

The name of the static/media GCS buckets


### GCS_CREDENTIALS

(See the Service Account section for details)

### Permissions

#### bucket permissions

* Add a new *user* ACL for the service account user (e.g.: `throw-away@thisn-000000.iam.gserviceaccount.com`


#### default object permissions

* Add a new *user* ACL for the service account user (e.g.: `throw-away@thisn-000000.iam.gserviceaccount.com`)
* Add a new *user* ACL for the special `allUsers` target (aka: anonymous) user. Assign the 'Reader' role.


### GCS Bucket CORS Configuration

For non-programmatic manipulation of GCS buckets use the [gsutil](https://cloud.google.com/storage/docs/gsutil_install) utility.

A basic CORS configuration looks like:


```json
[
  {
    "origin": ["https://this.domain.tld"],
    "responseHeader": ["Content-Type"],
    "method": ["GET"],
    "maxAgeSeconds": 3600
  }
]

```

Saved as `/tmp/cors.json` it can be attached to a bucket with `gsutil cors set /tmp/cors.json gs://my-bucket`


