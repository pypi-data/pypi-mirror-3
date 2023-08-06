#!/usr/bin/python
"""
A simple example of how to use Thermos with bottle.py, SQLAlchemy and
repoze.what

Creates a webserver on localhost:8080 with a username/password of admin/admin.
Needs login.tpl file.
"""

from bottle import route, run, app, get, post, abort, request, debug
from bottle import template, redirect

from repoze.what.plugins.quickstart import setup_sql_auth

from thermos.auth.models import User, Group, Permission, ThermosBase, translations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import logging, sys
import os
import pprint

@get('/')
def root():
    identity = request.environ.get('repoze.who.identity')
    if identity is None:
        return "<p>Not logged in. <a href='/login'>Login</a>"

    user = identity.get('repoze.who.userid')
    return "Logged in as %s. <a href='/logout_handler'>Logout</a>" % (user)

@route('/login')
def login():
    came_from = request.params.get("came_from") or "/"
    return template("login", came_from=came_from)

@route('/welcome_back')
def post_login():
    identity = request.environ.get('repoze.who.identity')
    if identity is None:
        return "<p>Username or password incorrect. <a href='/login'>Login</a>"

    came_from = request.params.get("came_from") or "/"

    return "<p>You are now logged in. <a href='/logout_handler'>Logout</a></p>"

@route('/see_you_later')
def post_login():
    return "<p>You are now logged out. <a href='/'>Home</a></p>"

def add_auth(app,session):

    return setup_sql_auth(app=app, user_class=User, group_class=Group,
        permission_class=Permission, dbsession=session,
        post_login_url='/welcome_back', post_logout_url='/see_you_later',
        translations=translations)
    
log_stream = None
if os.environ.get('WHO_LOG'):
    log_stream = sys.stdout

engine = create_engine('sqlite:///:memory:', echo=False)
ThermosBase.metadata.create_all(engine) 
Session = sessionmaker(bind=engine)
session = Session()

middleware = add_auth(app(),session)

admins = Group(u'admins')
session.add(admins)

admin = User(u'admin')
admin.set_password('admin')
admin.groups.append(admins)
session.add(admin)

session.commit()

run(app=middleware, host='0.0.0.0', port=8080, reloader=True)

