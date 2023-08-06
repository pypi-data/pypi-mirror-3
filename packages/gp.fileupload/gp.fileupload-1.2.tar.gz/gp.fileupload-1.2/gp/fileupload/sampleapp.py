# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import cgi
import time
from cStringIO import StringIO
from paste.deploy import CONFIG
from paste.deploy.config import ConfigMiddleware

def application(environ, start_response):
    if 'gp.fileupload.id' in environ['QUERY_STRING']:
        # process post here
        block_size = 1024
        length = int(environ['CONTENT_LENGTH'])
        blocks = [block_size for i in range(block_size, length, block_size)]
        blocks.append(length-len(blocks)*block_size)

        # read input and write to temp file
        consumed = 0
        rfile = environ['wsgi.input']
        data = ''
        for size in blocks:
            data += rfile.read(size)
        content = ['<html><body><h1>Files</h1>']
        if 'HTTP_STORED_PATHS' in environ:
            fields = cgi.FieldStorage(fp=StringIO(data),
                                      environ=environ,
                                      keep_blank_values=1)
            for key in fields.keys():
                filename = getattr(fields[key], 'filename', None)
                if filename:
                    content.append(
                            '<div>%s</div>' % filename)
        content.append('</body></html>')
        start_response('200 OK', [('Content-type', 'text/html')])
        return content

    start_response('200 OK', [('Content-type', 'text/html')])
    content = [
        '<html><head><title>File upload</title>\n',
        '<script type="text/javascript" src="/gp.fileupload.static/jquery.js"></script>\n',
        '<script type="text/javascript">\n',
        '   jQuery(document).ready(function() {\n',
        '       jQuery(\'#sample\').fileUpload({"debug":true});\n',
        '   });\n',
        '</script>\n',
        '</head>\n',
        '<body>\n',
        '\n',
        '<h1>File upload demo</h1>\n',
        '\n',
        '<h3>js sample</h3>\n',
        '<div id="sample">\n',
        '</div>\n',
        '\n',
        '<h3>html sample</h3>\n',
        '<form action="/upload" enctype="multipart/form-data">\n',
        '<input type="file" name="my_file" /><br />\n',
        '<input type="file" name="my_file2" /><br />\n',
        '<input type="submit" />\n',
        '</form>\n',
        '\n',
        '</body></html>',
        ]
    return content

def make_app(
    global_conf,
    **kw):
    app = application
    conf = global_conf.copy()
    conf.update(kw)
    app = ConfigMiddleware(app, conf)
    return app

