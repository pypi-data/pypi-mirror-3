# -*- coding: utf-8 -*-
"""
    app.wsgi
    ~~~~~~~~

    This wsgi script provides an example of how to use rs.application as
    WSGI application under mod_wsgi or similar WSGI server.

    mod_wsgi can be found at http://code.google.com/p/modwsgi

"""

import sys
import os

this_dir = os.path.dirname(__file__)

sys.path.insert(0, this_dir)

import logging

handler = logging.FileHandler(os.path.join(this_dir, 'app.log'))
handler.setFormatter(logging.Formatter("%(asctime)s  %(module)-1s  %(levelname)-5s - %(message)s"))

logger = logging.getLogger('rs')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

from app import application

# or
# import app
# application = app.application()