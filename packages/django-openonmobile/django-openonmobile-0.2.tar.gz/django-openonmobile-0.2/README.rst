===================
django-openonmobile
===================

Open current page on your mobile with a QR code.

- Main url: http://bitbucket.org/ferranp/django-openonmobile
- Documentation : http://readthedocs.org/docs/django-openonmobile


Features
========

- Creates a QR image with a url to redirect a phone user to the current image.
- The mobile phone user will be authenticats automatically with the same user.
- Uses the cache to keep the temporaty toker for authentication (so no database needed).


Installation
============

#. Add ``"openonmobile"`` directory to your Python path.
#. Add ``"openonmobile"`` to the ``INSTALLED_APPS`` tuple found in
   your settings file.
#. Add ``"openonmobile.middleware.AuthOnMobileMiddleware"`` to your
   ``MIDDLEWARE_CLASSES`` tuple found in your settings file.
#. Add ``"openonmobile.auth.AuthOnMobileBackend"`` to your
   ``AUTHENTICATION_BACKENDS`` tuple found in your settings file.
#. Include ``"openonmobile.urls"`` to your URLconf.





