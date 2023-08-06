# -*- coding: utf-8 -*-
# (c) 2008 Gael Pasgrimaud and contributors
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
import os
import logging
import tempfile

log = logging.getLogger('fileupload')

BASE_PATH = '/gp.fileupload.'
SESSION_NAME = 'gp.fileupload.id'
HTTP_STORED_PATHS = 'HTTP_STORED_PATHS'
HTTP_SERVE_PATH = 'HTTP_SERVE_PATH'
REPLACEMENT_CHAR = '_'

TEMP_DIR = os.path.join(tempfile.gettempdir(), 'fileUpload')

STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
VALID_FILES = [f for f in os.listdir(STATIC_DIR) if not f.startswith('.')]
