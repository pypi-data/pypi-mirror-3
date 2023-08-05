#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Gregory Sitnin <sitnin@gmail.com>"
__copyright__ = "Gregory Sitnin, 2011"


import functools
import logging


def https_only(method):
    """Decorate method with this to ensure request will be served only via HTTPS."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.protocol != "https":
            logging.warning("HTTPS only url requested via HTTP: %s"%self.request.full_url())
            self.redirect(self.request.full_url().replace("http", "https"))
        else:
            return method(self, *args, **kwargs)
    return wrapper

