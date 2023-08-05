Settings Reference
==================

.. contents:: :local:

.. _SECURE_CHECKS:

SECURE_CHECKS
-------------

A list of strings. Each string should be a Python dotted path to a function
implementing a configuration check that will be run by the :doc:`checksecure
management command <checksecure>`.

Defaults to::

    [
        "djangosecure.check.csrf.check_csrf_middleware",
        "djangosecure.check.sessions.check_session_cookie_secure",
        "djangosecure.check.sessions.check_session_cookie_httponly",
        "djangosecure.check.djangosecure.check_security_middleware",
        "djangosecure.check.djangosecure.check_sts",
        "djangosecure.check.djangosecure.check_frame_deny",
        "djangosecure.check.djangosecure.check_content_type_nosniff",
        "djangosecure.check.djangosecure.check_ssl_redirect",
    ]

.. _SECURE_FRAME_DENY:

SECURE_FRAME_DENY
-----------------

If set to ``True``, causes :doc:`middleware` to set the :ref:`x-frame-options`
header on all responses that do not already have that header (and where the
view was not decorated with the ``frame_deny_exempt`` decorator).

Defaults to ``False``.

.. _SECURE_HSTS_SECONDS:

SECURE_HSTS_SECONDS
-------------------

If set to a non-zero integer value, causes :doc:`middleware` to set the
:ref:`http-strict-transport-security` header on all responses that do not
already have that header.

Defaults to ``0``.

.. _SECURE_CONTENT_TYPE_NOSNIFF:

SECURE_CONTENT_TYPE_NOSNIFF
---------------------------

If set to ``True``, causes :doc:`middleware` to set the
:ref:`x-content-type-options` header on all responses that do not already
have that header.

Defaults to ``False``.

.. _SECURE_PROXY_SSL_HEADER:

SECURE_PROXY_SSL_HEADER
-----------------------

In some deployment scenarios, Django's ``request.is_secure()`` method returns
``False`` even on requests that are actually secure, because the HTTPS
connection is made to a front-end loadbalancer or reverse-proxy, and the
internal proxied connection that Django sees is not HTTPS. Usually in these
cases the proxy server provides an alternative header to indicate the secured
external connection. This setting, if set, should be a tuple of ("header",
"value"); if "header" is set to "value" in ``request.META``, django-secure will
tell Django to consider it a secure request (in other words,
``request.is_secure()`` will return ``True`` for this request). The "header"
should be specified in the format it would be found in ``request.META``
(e.g. "HTTP_X_FORWARDED_PROTOCOL", not "X-Forwarded-Protocol"). For example::

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTOCOL", "https")

Defaults to ``None``.

.. warning::

   If you set this to a header that your proxy allows through from the request
   unmodified (i.e. a header that can be spoofed), you are allowing an attacker
   to pretend that any request is secure, even if it is not. Make sure you only
   use a header that your proxy sets unconditionally, overriding any value from
   the request.

.. _SECURE_REDIRECT_EXEMPT:

SECURE_REDIRECT_EXEMPT
----------------------

Should be a list of regular expressions. Any URL path matching a regular
expression in this list will not be redirected to HTTPS, if
:ref:`SECURE_SSL_REDIRECT` is ``True`` (if it is ``False`` this setting has no
effect).

Defaults to ``[]``.

.. _SECURE_SSL_HOST:

SECURE_SSL_HOST
---------------

If set to a string (e.g. ``secure.example.com``), all SSL redirects will be
directed to this host rather than the originally-requested host
(e.g. ``www.example.com``). If :ref:`SECURE_SSL_REDIRECT` is ``False``, this
setting has no effect.

Defaults to ``None``.

.. _SECURE_SSL_REDIRECT:

SECURE_SSL_REDIRECT
-------------------

If set to ``True``, causes :doc:`middleware` to :ref:`redirect <ssl-redirect>`
all non-HTTPS requests to HTTPS (except for those URLs matching a regular
expression listed in :ref:`SECURE_REDIRECT_EXEMPT`).

.. note::

   If turning this to ``True`` causes infinite redirects, it probably means
   your site is running behind a proxy and can't tell which requests are secure
   and which are not. Your proxy likely sets a header to indicate secure
   requests; you can correct the problem by finding out what that header is and
   configuring the :ref:`SECURE_PROXY_SSL_HEADER` setting accordingly.

Defaults to ``False``.
