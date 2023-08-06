Django-iframe
=============

This is a set of tools/utilities gathered to be used in iframes for example
social network applications

Iframe fix middleware
=====================
middleware that fixes IE PS3 and Safari Cookie problems.

Usage
-----

Add new midleware after session creation::

    MIDDLEWARE_CLASSES = (
        ...
        'iframetoolbox.middleware.IFrameFixMiddleware',
        ...
    )

add iframetoolbox to installed apps::

    INSTALLED_APPS = (
        ...

        'iframetoolbox',
        ...
    )

add url config::

    url(r'^iframe/', include('iframetoolbox.urls')),


If needed overwrite templates with your message and style.
For refference look at source (download url).

TODO:
=====

Propper docs
