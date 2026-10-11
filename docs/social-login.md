# Social login (Google, Facebook)

Cell Cloud uses [django-allauth](https://docs.allauth.org/) for social login,
and [dj-rest-auth](https://dj-rest-auth.readthedocs.io/) to expose it to the
single page app (`POST /api/v1/auth/google/` and `/api/v1/auth/facebook/`
with the provider's `access_token`, or `code` for Google). These notes are
based on Weian Wang's 2016 setup notes (`django allauth settings.md` on the
`cellbase-dev` branch, #19).

## 1. Create the OAuth application at the provider

* **Google**: Google Cloud console → APIs & Services → Credentials → OAuth
  client ID (Web application).
  * *Authorized JavaScript origins*: your site, e.g. `https://hidos.io`.
  * *Authorized redirect URIs*: `https://<your site>/accounts/google/login/callback/`
    (development: `http://localhost:8000/accounts/google/login/callback/`).
* **Facebook**: Meta for Developers → create an app with Facebook Login;
  valid OAuth redirect URI `https://<your site>/accounts/facebook/login/callback/`.

## 2. Give the client id and secret to Cell Cloud

Either set environment variables:

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
FACEBOOK_CLIENT_ID=...
FACEBOOK_CLIENT_SECRET=...
```

or add them in the admin under *Social accounts → Social applications*. Pick
the provider, fill in the client id and secret, and add the site. The site is
`settings.SITE_ID` (1), whose domain is `SITE_DOMAIN` since the #78 data
migration. Don't do both for the same provider.

## 3. Use it

* Server-rendered pages: the `/login` page shows a *Log in with ...* button
  for every configured provider. allauth's own pages are under `/accounts/`.
* Single page app: get an access token from the provider's JavaScript SDK,
  then `POST /api/v1/auth/google/ {"access_token": "..."}`. The response is
  the same JWT as `/api/v1/auth/login/`.

Provider settings (scopes, Facebook API version, ...) are in
`SOCIALACCOUNT_PROVIDERS` in `hidos/settings/base.py`.
