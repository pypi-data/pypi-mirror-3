# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import cgi
import glob
import shutil
import doctest
from StringIO import StringIO
from paste.fixture import TestApp
from webob import Request, Response, exc
from nose import with_setup
from gp.fileupload.config import *
from gp.fileupload.upload import FileUpload
from gp.fileupload.storage import Storage
from gp.fileupload.resource import ResourceInjection
import gp.fileupload

def application(environ, start_response):
    resp = Response()
    resp.content_type = 'text/plain;charset=utf-8'
    if environ['PATH_INFO'] == '/test.txt':
        resp.body = environ['test_path']
        return resp(environ, start_response)

    data = [l for l in environ['wsgi.input'].readlines()]
    if len(data) > 0:
        resp.body = ''.join(data)
    else:
        resp.content_type = 'text/html;charset=utf-8'
        resp.body = '''<html>
<head>
</head>
<body>
Test Page
</body>
</html>'''
    return resp(environ, start_response)

BOUNDARY='--testdata'
ASSERT_DATA = '--%s' % BOUNDARY
TEST_DATA = '''--%s
Content-Disposition: form-data; name="my_file"; filename="test.js"
Content-Type: application/x-javascript

var test = null;

--%s
Content-Disposition: form-data; name="my_file2"; filename="text.txt"
Content-Type: text/plain

some text a little bit longer than the minimum

--%s--
''' % (BOUNDARY, BOUNDARY, BOUNDARY)

TEST_POST_DATA = (
    ('my_file', 'test.js', 'var test = null;\n'),
    ('my_file2', 'test.txt', 'some text a little bit longer than the minimum\n'))

TEST_LENGTH = str(len(TEST_DATA))
TEMP_DIR = tempfile.mkdtemp()

def setup_func():
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.mkdir(TEMP_DIR)

def teardown_func():
    if os.path.isdir(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

def test_injection():
    app = TestApp(ResourceInjection(application,
                                      ['fileupload.css',
                                        'jquery.fileupload.js']))
    response = app.get('/')
    assert '/gp.fileupload.static/jquery.fileupload.js' in response, response
    assert '/gp.fileupload.static/fileupload.css' in response, response

@with_setup(setup_func, teardown_func)
def test_static_content():
    app = TestApp(FileUpload(application, tempdir=TEMP_DIR))
    response = app.get('/gp.fileupload.static/fileupload.css')
    assert '.fuProgress' in response, response

@with_setup(setup_func, teardown_func)
def test_stat():
    app = TestApp(FileUpload(application, tempdir=TEMP_DIR))
    response = app.get('/gp.fileupload.stat/1')
    assert "{'state': 0, 'percent': 0}" in response, response

@with_setup(setup_func, teardown_func)
def test_upload():
    shutil.rmtree(TEMP_DIR)

    app = TestApp(FileUpload(application, tempdir=TEMP_DIR, max_size=400))

    # upload a file
    response = app.post('/?gp.fileupload.id=1',
                        upload_files=TEST_POST_DATA)
    assert 'Content-Disposition: form-data; name="my_file"; filename="test.js"' in response, response

    # get stats
    response = app.post('/gp.fileupload.stat/1')
    assert "{'state': 1, 'percent': 100}" in response, response

    # check temp files
    tempfiles = glob.glob(os.path.join(TEMP_DIR, '*'))
    assert len(tempfiles) == 0, tempfiles

    # check max size
    try:
        response = app.post('/?gp.fileupload.id=1',
                            upload_files=(('test_file', 'test.txt', '_'*500),))
    except Exception, e:
        assert 'File is too big' in str(e), str(e)

@with_setup(setup_func, teardown_func)
def test_storage():

    app = Storage(application, TEMP_DIR, tempdir=TEMP_DIR,
                  exclude_paths=['/@@'], max_size=500)

    # upload a file
    req = Request.blank('/')
    req.method = 'POST'
    req.content_type = 'multipart/form-data;boundary="%s"' % BOUNDARY
    req.body = TEST_DATA
    response = req.get_response(app)

    assert response.status.split()[0] == '200'

    # get fields from output
    req.body = response.body
    fields = cgi.FieldStorage(fp=StringIO(req.body),
                              environ=req.environ,
                              keep_blank_values=1)

    # retrieve valid file path
    assert 'my_file' in fields.keys(), (req.environ, response.body)
    field = fields['my_file']
    path = os.path.join(TEMP_DIR, field.file.read().strip())
    assert os.path.isfile(path) is True, path

    # check file content
    data = open(path).read()
    assert data.strip() == 'var test = null;', data

    # now check get
    req = Request.blank('/test.txt')
    req.environ['test_path'] = path
    response = req.get_response(app)

    # check correct output
    assert 'var test = null;' in response.body, response.body

    # check temp files
    tempfiles = glob.glob(os.path.join(TEMP_DIR, '*.dump'))
    assert len(tempfiles) == 0, tempfiles

    # check max size
    try:
        response = TestApp(app).post('/?gp.fileupload.id=1',
                                    upload_files=(('test_file', 'test.txt', '_'*500),))
    except Exception, e:
        assert 'File is too big' in str(e), str(e)

###############
## Doc tests ##
###############

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)

dirname = os.path.join(os.path.dirname(gp.fileupload.__file__), '..', '..', 'docs')


def build_testcase(filename):
    name = os.path.splitext(filename)[0]
    name = name.replace('-', '_')
    path = os.path.join(dirname, filename)

    class Dummy(doctest.DocFileCase):
        def __init__(self, *args, **kwargs):
            # get tests from file
            parser = doctest.DocTestParser()
            doc = open(self.path).read()
            test = parser.get_doctest(doc, globals(), name, self.path, 0)

            # init doc test case
            doctest.DocFileCase.__init__(self, test, optionflags=optionflags)

        def setUp(self):
            """init globals
            """
            setup_func()
            test = self._dt_test

        def tearDown(self):
            """cleaning
            """
            test = self._dt_test
            test.globs.clear()
            teardown_func()

    # generate a new class for the file
    return ("Test%s" % name.title(),
            type('Test%sClass' % name.title(), (Dummy,), dict(path=path)))

for filename in os.listdir(dirname):
    if filename.endswith('.txt'):
        name, klass = build_testcase(filename)
        exec "%s =  klass" % name

# clean namespace to avoid test duplication   
del build_testcase, filename, name, klass


