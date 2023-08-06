# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import re
import glob
from webob import Request
from gp.fileupload.config import *

CSS_TEMPLATE = \
'<style type="text/css"><!-- @import url(%%(SCRIPT_NAME)s/gp.fileupload.static/%s); --></style>'

JS_TEMPLATE = \
'<script type="text/javascript" src="%%(SCRIPT_NAME)s/gp.fileupload.static/%s"></script>'

class ResourceInjection(object):
    """This middleware inject some javascript and css to an html page
    """

    def __init__(self, application, include_files=[], static_dir=None):

        self.application = application

        if not static_dir:
            static_dir = STATIC_DIR

        # existing files
        files = [f for f in os.listdir(static_dir) if not f.startswith('.')]

        valid_files = []
        # analyze patterns and filter valid files
        for pattern in include_files:
            if '*' in pattern:
                filenames = sorted(glob.glob(
                                        os.path.join(static_dir, pattern)),
                                   reverse=True)
                filenames = [os.path.split(f)[1] for f in filenames]
            else:
                filenames = pattern in files and [pattern] or []
            valid_files.extend(filenames)

        # generate tags
        self.js = self.css = ''
        for f in valid_files:
            if f.endswith('.css'):
                self.css += CSS_TEMPLATE % f
            elif f.endswith('.js'):
                self.js += JS_TEMPLATE % f
        log.info('%s will be injected in html', ', '.join(valid_files))

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = req.get_response(self.application)
        status = resp.status.split()[0]
        ctype = resp.content_type
        if status == '200' and ctype.startswith('text/html'):
            resp.body = self.add_to_end(resp.body, environ)

        return resp(environ, start_response)

    _end_body_re = re.compile(r'</body.*?>', re.I|re.S)
    _start_head_re = re.compile(r'<head.*?>', re.I|re.S)

    def add_to_end(self, html, environ):
        """
        Adds extra_html to the end of the html page (before </body>)
        """
        js = self.js % environ
        css = self.css % environ

        match = self._start_head_re.search(html)
        if match:
            html = html[:match.end()] + css + html[match.end():]

        match = self._end_body_re.search(html)
        if match:
            html = html[:match.start()] + js + html[match.start():]
        return html
