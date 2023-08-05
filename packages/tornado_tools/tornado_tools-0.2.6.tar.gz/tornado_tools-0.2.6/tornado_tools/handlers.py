#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Gregory Sitnin <sitnin@gmail.com>"
__copyright__ = "Gregory Sitnin, 2011"


import tornado.web
import logging
from pprint import pformat


class AppStatus(tornado.web.RequestHandler):
    def test(self, reply):
        reply["warnings"].append("Webapp status tests are not implemented, yet")

    def get(self, format):
        reply = {"overall": True, "info": list(), "warnings": list(), "errors": list()}

        reply["info"].append({"tornado": tornado.version})

        self.test(reply)

        if format == "json":
            self.set_header("Content-Type", "application/json")
            self.write(json.dumps(reply))
        else:
            self.set_header("Content-Type", "text/plain")
            self.write(pformat(reply))


AppStatusUrl = (r"/status\.(json|txt)", AppStatus)
