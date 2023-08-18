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

## TODO ideas


1. Codebase improvements
* Refactoring LLM/embedding code to be more platform independent
* Django websockets with HTMX-ws, OR...
* (big task) Front-end (React? Vue?) + API-only backend
  * Could ultimately simplify controller (django "views")


1. File upload UI
* Allow multiple files at once
* Speed (direct upload to GCP via storage API?)
  * Currently its routed through Django-Storage
* Progress indicators
* ~User-specific prefixes in filename to prevent clashes~
* Duplicate filename handling:
  * Prompt to create new or Update existing
  * Add extra characters (built in functionality)
  * Always store original filename in Model
  * OR Update existing (overwrite file, update Model)
* Warn user if document already uploaded and viewable
  * See item (7) below

1. Extraction
* Quality (how does the text look? Extract to markdown?)
* More file types
* Separate from upload function?

1. Indexing
* Robustness (keep doing it even if user navigates away)
* Speed (parallelize? if rate limits aren't the issue)
* Extract titles (task-specific model, not LLM?)
* Generate tags (task-specific model, not LLM?)
* Make use of existing metadata when possible
* Speed up full text retrieval
  * Store text in Document rather than DocumentChunks
  * @property in chunk to retrieve text from Document
  * Save CHUNK_SIZE property in Document model

1. Retrieval
* Similarity search should be augmented
* Keyword search
* Add document titles/summaries etc. into chunks!
* Increase chunk size / overlap
* Tweak distance metrics / thresholds
  * Multiply chunk distance by document summary distance?
  * Try other distance metrics?

1. Q&A chat performance
* Prompt chain (prompt, stuffing vs. map-reduce, etc)
* Reduce hallucinations
* Improve display of sources
* ~Try chat model vs. text model~
  * Text model is better
* Select individual docs or tags
* Option to include full text of selected docs in context
  * (as opposed to similarity search for context)

1. Chat UI
* ~Session, chat, or **user** settings modal~
  * ~Select model (chat vs. code-chat model)~
  * ~Modify system prompt~
  * ~(Advanced) modify params (temp, tokens)~
* Share chat
* Right sidebar: enable document Q&A, select docs/tags
  * Or enter URL
* Clean up empty chats in DB
  * Prevent creation of empty chats?
  * Delete empty chats in cron job?

1. Document management
* Private vs. shared (all-users) access
* Ability to delete files (after filename clashes resolved, see 1.)
* Edit titles, summary, tags
  * Keep track of human-edited vs. generated metadata
* View shared files
  * Shouldn't be able to modify tags, etc. when not owner?
* "Star" files from all-users access?
* Search/filter documents in document management view
  * Will become necessary if there are 100+ documents
* "Find similar documents"
* How to integrate with official IM repositories?
  * This could become an IM issue if widely used
* Hide embeddings, similarity search from most users
  * unless User setting for "power user"
* Hide document Q&A field once implemented in Chat UI
* Online sources (webpage URLs, crawl from URL, youtube link, arxiv)...

1. Integrated help
* Show tour of application if new user
  * "Don't show this again" checkbox
* Draw attention to:
  * "New chat" button
  * Old chats appear in left sidebar
    * Delete old chats
  * Settings (once implemented)
  * Right sidebar (once implemented)
  * My documents tab
    * Upload documents
    * Expand documents / edit metadata

1. French
* French UI is doable; normal Django translation task
* How good are the LLMs in French?
  * Do French queries surface English content, and vice-versa?
* System prompts, LangChain internal prompts etc. may need modification
  * Bot should respond in user's selected language
* Language tagging of documents / chunks / elements
  * Multi-lang documents? (very common in PDFs)
  * Preserve language tagging where it exists? (e.g. HTML, Word, PDF)
* French document summaries
* French full-text
* Likely issues:
  * multi-lang tags (generate both? Translate?)
  * search retrieves duplicates due to multi-lang

1.  Sharing prompts / chains
* allow users to refine, share (system) prompts for different tasks
  * e.g. writing editor prompt
  * translation
  * reformat input text as list, JSON, etc.
  * extract action items with names from meeting notes
* Share system prompts with link (prompt in URL?)
* Prompt browser UI (SystemPrompt objects in DB or 2-message chat?)
* Extensibility with different chain endpoints (in codebase)
  * But common UI to call different chains
  * The document search chain(s) could be the first 2?
