# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
from webob import Request, Response, exc
from paste.fileapp import FileApp
from gp.fileupload.config import *
from gp.fileupload.resource import *
from gp.fileupload.storage import *

try:
    import json
except ImportError:
    import simplejson as json

__all__ = ['FileUpload', 'make_app']



class InputWrapper(object):

    def __init__(self, rfile, sfile):
        log.debug('InputWrapper init: %s, %s', rfile, sfile)
        self._InputWrapper_rfile = rfile
        self._InputWrapper_sfile = sfile
        self._InputWrapper_size = 0
        for k in ('flush', 'write', 'writelines', 'close'):
            if hasattr(rfile, k):
                setattr(self, k, getattr(rfile, k))

    def _flush(self, chunk):
        length = len(chunk)
        if length > 0:
            self._InputWrapper_size += length
            self._InputWrapper_sfile.seek(0)
            self._InputWrapper_sfile.write(str(self._InputWrapper_size))
            self._InputWrapper_sfile.flush()
        return chunk

    def __iter__(self):
        riter = iter(self._InputWrapper_rfile)
        def wrapper():
            for chunk in riter:
                yield self._flush(chunk)
        return iter(wrapper())

    def read(self, size=None):
        if size is not None:
            chunk = self._InputWrapper_rfile.read(size)
        else:
            chunk = self._InputWrapper_rfile.read()
        return self._flush(chunk)

    def readline(self, size=None):
        if size is not None:
            chunk = self._InputWrapper_rfile.readline(size)
        else:
            chunk = self._InputWrapper_rfile.readline()
        return self._flush(chunk)

    def readlines(self, size=None):
        if size is not None:
            chunk = self._InputWrapper_rfile.readlines(size)
        else:
            chunk = self._InputWrapper_rfile.readlines()
        return self._flush(chunk)

class FileUpload(object):
    """A middleware class to handle POST data and get stats on the file upload
    progress:

        >>> FileUpload(app)

    """

    def __init__(self, application, tempdir=TEMP_DIR,
                 max_size=None, require_session=False):
        self.application = application
        if not tempdir:
            self.tempdir = TEMP_DIR
        else:
            self.tempdir = tempdir
        if not os.path.isdir(tempdir):
            os.makedirs(tempdir)
        log.info('Temporary directory: %s' % tempdir)

        self.max_size = max_size
        if max_size:
            log.info('Max upload size: %s' % max_size)

        self.require_session = require_session

    def __call__(self, environ, start_response):
        req = Request(environ)
        path_info = req.path_info

        if BASE_PATH in path_info:
            if BASE_PATH+'stat/' in path_info:
                # get stats
                return self.status(req)(environ, start_response)
            elif BASE_PATH+'static/' in path_info:
                # static file
                filename = path_info.split('/')[-1]
                if filename in VALID_FILES:
                    path = os.path.join(STATIC_DIR, filename)
                    return FileApp(path)(environ, start_response)

        elif environ['REQUEST_METHOD'] == 'POST':
            if (not self.require_session or
                SESSION_NAME in environ.get('QUERY_STRING', '')):
                return self.upload(req)(environ, start_response)

        return self.application(environ, start_response)

    def tempfiles(self, session, environ):
        return (os.path.join(self.tempdir, session+'.size'),
               os.path.join(self.tempdir, session+'.stats'))

    def upload(self, req):
        session = req.GET.get(SESSION_NAME)

        if not session.isdigit():
            log.error('Malformed session id "%s"', session)
            return exc.HTTPServerError('Malformed session id:%s' % session)

        req.environ[SESSION_NAME] = session
        tempfile, statfile = self.tempfiles(session, req.environ)
        length = req.content_length
        if self.max_size and int(length) > self.max_size:
            log.error('File too big in session "%s"', session)
            sfile = open(statfile, 'w')
            sfile.write('-1')
            sfile.close()
            return exc.HTTPServerError('File is too big')

        log.debug('Start session "%s", length: %s', session, length)
        sfile = open(statfile, 'w')
        sfile.write(str(length))
        sfile.close()

        sfile = open(tempfile, 'w')
        req.environ['wsgi.input'] = InputWrapper(
                                    req.environ['wsgi.input'],
                                    sfile)
        resp = req.get_response(self.application)
        sfile.close()

        # remove temp file
        os.remove(tempfile)

        return resp

    def status(self, req):
        session = req.path_info.split('/')[-1]

        if not session.isdigit():
            log.error('Malformed session id "%s"', session)
            return exc.HTTPServerError('Malformed session id:%s' % session)

        tempfile, statfile = self.tempfiles(session, req.environ)
        if os.path.isfile(tempfile):
            sfile = open(statfile, 'r')
            length = int(sfile.read())
            sfile.close()

            if length == -1:
                # file is too big
                data = dict(state=-1, percent=0, size=0, length=length)
                os.remove(statfile)
            else:
                # return progress
                try:
                    size = int(open(tempfile).read())
                except ValueError:
                    # file is not written yet
                    data = dict(state=0, percent=0, size=0, length=length)
                else:
                    data = dict(state=1,
                                percent=int(float(size)/length*100),
                                size=size,
                                length=length)
        elif os.path.isfile(statfile):
            sfile = open(statfile, 'r')
            length = int(sfile.read())
            sfile.close()
            if length == -1:
                # file is too big
                data = dict(state=-1, percent=0, size=0, length=length)
            else:
                # upload finished
                data = dict(state=1, percent=100, size=length, length=length)
            os.remove(statfile)
        else:
            # bad state
            data = dict(state=0,
                        percent=0,
                        size=0,
                        length=0)

        log.debug('%s: %s', session, data)
        resp = Response()
        resp.content_type = 'application/json'
        if 'callback' in req.GET:
            resp.body = req.GET['callback'] + '(' + json.dumps(data) + ')'
        else:
            resp.body = json.dumps(data)
        return resp

def make_app(application, global_conf, tempdir=None, max_size=0,
             upload_to=None, exclude_paths=None, include_files=None,
             require_session=False):
    """build a FileUpload application
    """

    if not tempdir:
        tempdir = TEMP_DIR
    else:
        tempdir = os.path.normpath(tempdir)

    if max_size:
        # use Mo
        max_size = int(max_size)*1024*1024

    if require_session in ['true', 'True']:
        require_session = True
    else:
        require_session = False

    if upload_to:
        upload_to = os.path.normpath(upload_to)
        if exclude_paths is None:
            exclude_paths = []
        else:
            if isinstance(exclude_paths, basestring):
                exclude_paths = [os.path.normpath(f) for f
                                 in exclude_paths.split(' ') if f]
        application = Storage(
            application, upload_to, tempdir, exclude_paths,
            max_size=max_size, require_session=require_session)

    if include_files:
        if isinstance(include_files, basestring):
            include_files = [os.path.normpath(f) for f
                             in include_files.split(' ') if f]
        application = ResourceInjection(application, include_files)

    return FileUpload(
        application, tempdir=tempdir,
        max_size=max_size, require_session=require_session)
