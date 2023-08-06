# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import re
import cgi
import sha
import stat
import shutil
import string
import datetime
from cStringIO import StringIO
from paste.fileapp import FileApp
from webob import Request, Response, exc
from gp.fileupload.config import *

__all__ = ['Storage']

allowed_letters = string.digits + string.ascii_letters + '_-'

def make_dir(root, session, environ):
    i = len(session)/3
    args = [session[:i], session[i:i*2], session[i*2:]]
    if 'REMOTE_USER' in environ:
        user = environ['REMOTE_USER']
        user = user.replace('@', '_at_')
        user = user.replace('.', '_')
        user = user.replace(' ', '_')
        user = ''.join([l for l in user if l in allowed_letters])
        args.insert(0, user)
    path = os.path.join(root, *args)
    return path

ERROR = 'gp.fileupload.error'
PURGE = 'gp.fileupload.purge'

def purge_files(environ, *paths):
    """remove files from the storage directory
    """
    meth = environ[PURGE]
    meth(*paths)

class Storage(object):
    """A middleware class to handle post request and store uploaded files to the
    specified directory and then pass the new file path to the application.
    """

    def __init__(self, application, upload_to, tempdir=None,
                 exclude_paths=None, max_size=0, require_session=False):
        self.application = application

        if not os.path.isdir(upload_to):
            os.makedirs(upload_to)
        self.upload_to = upload_to

        if not tempdir:
            tempdir = TEMP_DIR
        if not os.path.isdir(tempdir):
            os.makedirs(tempdir)
        self.tempdir = tempdir

        if exclude_paths:
            self.exclude_paths = [re.compile(p) for p in exclude_paths]
        else:
            self.exclude_paths = None

        self.max_size = max_size
        self.require_session = require_session

    def __call__(self, environ, start_response):
        req = Request(environ)
        if self.exclude_paths and req.method in ('GET', 'HEAD'):
            req = Request(environ)
            for p in self.exclude_paths:
                if p.search(req.path_info):
                    return self.application(environ, start_response)

            resp = req.get_response(self.application)
            status = resp.status.split()[0]
            ctype = resp.content_type

            if status == '200' and not ctype.startswith('text/html'):
                # file path can't be > 255
                if resp.content_length < 255:
                    rpath = resp.body.strip()
                    path = os.path.join(self.upload_to, rpath)
                    if os.path.isfile(path):
                        log.info('Serving %s' % path)
                        return FileApp(path)(environ, start_response)

            return resp(environ, start_response)

        elif req.method == 'POST':
            if (not self.require_session or
                SESSION_NAME in environ.get('QUERY_STRING', '')):
                return self.store(req)(environ, start_response)

        return self.application(environ, start_response)

    def store(self, req):
        """store file and change wsgi input
        """
        # Don't use the session to generate file path.
        # Use sha instead to get more directories
        session = sha.new(str(datetime.datetime.now())).hexdigest()

        # need to consume so see how many block we have to read
        length = req.content_length
        if length > self.max_size:
            return exc.HTTPServerError('File is too big')

        bsize = 4096
        if length < bsize:
            blocks = [length]
        else:
            blocks = [bsize for i in range(bsize, length, bsize)]
            blocks.append(length-len(blocks)*bsize)

        # read input an write to a temporary file
        dpath = os.path.join(self.tempdir, session+'.dump')
        dfile = open(dpath, 'w')
        rfile = req.environ['wsgi.input']

        for size in blocks:
            chunk = rfile.read(size)
            dfile.write(chunk)
            dfile.flush()
        dfile.close()

        # get form from file
        dfile = open(dpath)
        fields = cgi.FieldStorage(fp=dfile,
                                  environ=req.environ,
                                  keep_blank_values=1)

        # get directory
        session = session[0:6]
        relative = make_dir('', session, req.environ)
        dirname = make_dir(self.upload_to, session, req.environ)

        # store files on fs
        files = []
        fields_length = fields.length
        if fields_length:
            for key in fields.keys():
                field_list = fields[key]
                # handle multiple fields of same name (html5 uploads)
                if type(field_list) is not type([]):
                    field_list = [field_list]
                for field in field_list:
                    if isinstance(field, cgi.FieldStorage):
                        filename = field.filename
                        if filename:
                            # IE may pass files with full Windows path 
                            if '\\' in filename:
                                filename = filename.rsplit('\\', 1)[-1]
                            if '/' in filename:
                                filename = filename.rsplit('/', 1)[-1]
                            filename = filename.replace(':', REPLACEMENT_CHAR)
                            if filename == '':
                                filename = REPLACEMENT_CHAR
                            fd = field.file
                            if not os.path.isdir(dirname):
                                os.makedirs(dirname)
                            path = os.path.join(dirname, filename)
                            tempfile = open(path, 'w')
                            shutil.copyfileobj(fd, tempfile)
                            tempfile.close()
                            rpath = os.path.join(relative, filename)
                            files.append((filename, rpath, path))

        # prepare new input by replacing files contents
        rfile = StringIO()
        dfile.seek(0)

        if fields_length:
            jump = 0
            while dfile.tell() < length:
                line = dfile.readline()
                if line.startswith('Content-Disposition:'):
                    for filename, rpath, path in files:
                        if filename in line:
                            jump = os.stat(path)[stat.ST_SIZE]
                            break
                elif not line.strip() and jump:
                    dfile.seek(dfile.tell() + jump)
                    jump = 0
                    rfile.write(line)
                    rfile.write('%s\r\n' % rpath)
                    continue
                rfile.write(line)
        else:
            rfile.write(dfile.read())

        # remove temp file
        dfile.close()
        os.remove(dpath)

        # update content-length from new input
        req.content_length = rfile.tell()

        # replace input
        rfile.seek(0)
        input = req.environ['wsgi.input']
        req.environ['wsgi.input'] = rfile

        # add files path to environ
        paths = ':'.join([r for f, r, p in files])
        log.debug('Stored: %s', paths)
        req.environ[HTTP_STORED_PATHS] = paths

        # remove paths returned by the application
        def purge(*args):
            """helper function to remove old files
            """
            for path in args:
                path = os.path.join(self.upload_to, path)
                if os.path.isfile(path):
                    os.remove(path)
                    log.info('Purge: %s' % path)
        req.environ[PURGE] = purge

        resp = req.get_response(self.application)

        # We have to test the response status.
        # 2XX and 3XX status as successes.
        # Clients error or Servers error (4XX and 5XX)
        # will trigger the file deletion.
        status = resp.status.split()[0]
        if status[0] not in '23':
            for f,n,p in files:
                os.remove(p)

        # restore input
        req.environ['wsgi.input'] = input

        return resp

def make_app(application, global_conf, tempdir=None,
             upload_to=None, exclude_paths=None):
    """wrap an application with a `Storage` middleware
    """

    if not tempdir:
        tempdir = TEMP_DIR
    else:
        tempdir = os.path.normpath(tempdir)

    if not upload_to:
        raise ValueError('You must provide an upload directory')
    upload_to = os.path.normpath(upload_to)

    if exclude_paths is None:
        exclude_paths = []
    else:
        if isinstance(exclude_paths, basestring):
            exclude_paths = [os.path.normpath(f) for f
                             in exclude_paths.split(' ') if f]

    return Storage(application, upload_to, tempdir, exclude_paths)

