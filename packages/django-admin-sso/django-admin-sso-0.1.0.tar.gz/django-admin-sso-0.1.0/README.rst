================
Django admin SSO
================
Django admin SSO lets users login to a django admin using an openid provider. It
then looks up the email address of the new user and looks up the rights for him.

Installation
------------

1. Make sure you have a working django project setup.
2. Install django-admin-sso using pip::

    pip install django-admin-sso

3. Install dependencies:

    * python-openid>=2.2.5

3. Add `admin_sso` to installed apps in your `settings.py` file
4. Add the django-admin authentication backend::

    AUTHENTICATION_BACKENDS = (
        'admin_sso.auth.DjangoSSOAuthBackend',
        'django.contrib.auth.backends.ModelBackend',
    )

5. Run syncdb to create the needed database tables.
