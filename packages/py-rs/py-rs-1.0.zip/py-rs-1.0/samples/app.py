#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    app
    ~~~

    Just a sample app.

    Usage:

      Run app.py

      Go to http://localhost:8001

"""

import os.path
import functools

import rs


HTML = """
<HTML>
 <HEAD>
  <TITLE>{title}</TITLE>
 </HEAD>
 <BODY>
  {body}
 </BODY>
</HTML>
""".strip()


INDEX_BODY = """
<P>{p}</P>
<FORM action='/submit' method='POST'>
  <P>
    First name: <INPUT type="text" name="firstname" /><BR/>
    Last name: <INPUT type="text" name="lastname" /><BR/>
    email: <INPUT type="text" name="email"/> <BR/>
    <INPUT type="radio" name="sex" value="Male"/> Male<BR/>
    <INPUT type="radio" name="sex" value="Female"/> Female<BR/>
    <INPUT type="submit" value="Send"/> <INPUT type="reset"/>
  </P>
</FORM>
"""

FORM_BODY = """
<P>{0} {1}</P>
<P>{2}</P>
<P>{3}</P>
"""

TITLE = "Let's rock!"

this_dir = os.path.dirname(__file__)
mappath = functools.partial(os.path.join, this_dir)

@rs.get
def default():
    return '', 301, {'Location':'/index.html'}


@rs.get
@rs.path('index.html')
@rs.produces('text/html; charset=utf-8')
def index(p=rs.context.alias('say', default='')):
    return HTML.format(title=TITLE,
                       body=INDEX_BODY.format(p=p))


@rs.get
@rs.path('favicon.ico')
@rs.produces('image/png')
def favicon():
    with open(mappath('RS-ICON-LOGO.png'), 'rb') as fp:
        return fp.read()


@rs.post
@rs.path('submit')
@rs.produces('text/html; charset=utf-8')
def submit(firstname, lastname, email, sex):
    return HTML.format(title=TITLE,
                       body=FORM_BODY.format(firstname,
                                             lastname,
                                             email,
                                             sex))


application = rs.application()


if '__main__' == __name__:
    print 'Welcome'
    application.run('', 8001)
