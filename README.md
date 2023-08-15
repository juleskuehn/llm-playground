# llm-playground
I somewhat followed the tutorial at https://cloud.google.com/python/django/appengine to deploy to GCP app engine.

Some aspects of this repo are based on other PHAC Django projects, e.g. the base jinja template.

## Issues and fixes

### Secrets

Creating the secret required some fiddling due to org-level settings.

Also the secret came out in UTF-16 and wouldn't decode. Set the SECRET_KEY manually in the gcp.env before running the following commands.
```bash
gcloud secrets create django_settings --data-file .env --locations=us-east1 --replication-policy=user-managed
gcloud secrets add-iam-policy-binding django_settings --member serviceAccount:phx-datasciencellm@appspot.gserviceaccount.com --role roles/secretmanager.secretAccessor
```

Note that there is a `gcp.env` and a local `.env`. More about this later.

### APPENGINE_URL env variable

The tutorial says to update the `APPENGINE_URL` in `app.yaml` to `https://<project-name>.uc.r.appspot.com`. However, if you have deployed to a region other than US central ("uc") then this will fail. Ensure to copy the actual URL from your browser's address bar. In my case, it was "ue" (US East), not "uc".

### Sending emails to GC addresses

Sending login emails through SMTP (SendGrid) works for gmail addresses, but is blocked by GC M365 filtering.

A second option is to use GC Notify for email sending. But GC Notify emails *also* get sent to Junk Mail by M365. And the M365 link checking invalidates the magic links unless you disable a number of security features in `settings.py`:

```python
MAGICLINK_TOKEN_USES = 3  # M365 "clicks" links to check them, so must be > 1
MAGICLINK_REQUIRE_SAME_IP = False  # Otherwise M365 checks will invalidate token
MAGICLINK_REQUIRE_SAME_BROWSER = False  # As above
```

The third method (that actually works!) is to use Power Automate to send the email. These go straight to the inbox within a few seconds. Sometimes the M365 link-checking seems to invalidate the link from this method, so best to leave the settings as above.

### requirements.txt

GCP expects requirements.txt to be in the root of the django project, rather than in the repo root.

## .env

The `.env` files should be in the repo root directory. It is not used directly for GCP, but rather the contents of the file are stored in a secret. The file is almost the same for both local dev and GCP secret.

GCP version (`gcp.env`)

```env
DATABASE_URL=postgres://(get this from gcp...)
GS_BUCKET_NAME=(create a bucket for document uploads in GCP storage)
SECRET_KEY=...(something random)
GC_NOTIFY_API_KEY=...
GC_NOTIFY_TEMPLATE_ID=...
POWER_AUTOMATE_URL=https://...
```

For local development, just copy `gcp.env` to `.env` and add this line:

```
USE_CLOUD_SQL_AUTH_PROXY=True
```

Before running the django server, start the cloud-sql-proxy as described in the tutorial. I needed to add the `-g` flag:

```
cloud-sql-proxy -g phx-datasciencellm:us-east1:llm-playground
```