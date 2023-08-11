# llm-playground
Somewhat followed tutorial at https://cloud.google.com/python/django/appengine to deploy to GCP app engine.

## Issues and fixes

### Secrets

Creating the secret required some fiddling due to org-level settings.

Also the secret came out in UTF-16 and wouldn't decode. Set the SECRET_KEY manually in the .env before running the following command.
```
gcloud secrets create django_settings --data-file .env --locations=us-east1 --replication-policy=user-managed
```

### APPENGINE_URL env variable

The tutorial says to update the `APPENGINE_URL` in `app.yaml` to `https://<project-name>.uc.r.appspot.com`. However, if you have deployed to a region other than US central ("uc") then this will fail. Ensure to copy the actual URL from your browser's address bar. In my case, it was "ue" (US East), not "uc".

### Sending emails to GC addresses

Sending login emails through SMTP (SendGrid) works for gmail addresses, but is blocked by GC M365 filtering. Therefore, I've modified the PhacOnlyLoginView to use GC Notify for email sending.

However, GC Notify emails *still* get sent to Junk Mail by M365. And the link checking also invalidates the magic links unless you disable a number of security features in `settings.py`:

```python
MAGICLINK_TOKEN_USES = 3  # M365 "clicks" links to check them, so must be > 1
MAGICLINK_REQUIRE_SAME_IP = False  # Otherwise M365 checks will invalidate token
MAGICLINK_REQUIRE_SAME_BROWSER = False  # As above
```

The current solution (that actually works!) is to use Power Automate to send the email. These go straight to the inbox within a few seconds.

