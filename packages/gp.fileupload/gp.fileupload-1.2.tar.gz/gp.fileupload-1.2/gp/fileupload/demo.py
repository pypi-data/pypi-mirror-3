# -*- coding: utf-8 -*-
from gp.fileupload import make_app
import os

class FileUploadDemo(object):
    """Wrap a `paste.urlparser.StaticURLParser` to consume stdin if needed
    """

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST':
            if 'gp.fileupload.id' in environ['QUERY_STRING']:
                # need to consume so see how many block we have to read
                bsize = 1024
                length = int(environ['CONTENT_LENGTH'])
                print 'upload', length
                blocks = [bsize for i in range(bsize, length, bsize)]
                blocks.append(length-len(blocks)*bsize)

                # read input an write to /dev/null :)
                rfile = environ['wsgi.input']
                [rfile.read(size) for size in blocks]

            # StaticURLParser only deserve GET
            environ['REQUEST_METHOD'] = 'GET'

        return self.application(environ, start_response)

def make_demo(app, global_conf, **local_conf):
    upload_app = make_app(FileUploadDemo(app), {},
                   max_size='2',
                   tempdir=os.path.join('/tmp', 'fileuploaa_ddemo'),
                   include_files=['fileupload.css',
                                  'jquery.fileupload.*'])
    def application(environ, start_response):
        if '/gp.fileupload/demo.html' in environ['PATH_INFO']:
            return upload_app(environ, start_response)
        elif '/gp.fileupload.' in environ['PATH_INFO']:
            return upload_app(environ, start_response)
        else:
            return app(environ, start_response)
    return application
