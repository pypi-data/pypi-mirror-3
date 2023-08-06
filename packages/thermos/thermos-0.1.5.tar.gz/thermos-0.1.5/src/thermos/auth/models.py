"""
Thermos is a simple Django-like user-management system, designed to be used
with bottle.py, SQLAlchemy and repoze.what.

Licence: GPL3

    Copyright (C) 2012  Paul Dwerryhouse

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

__author__ = "Paul Dwerryhouse"
__licence__ = "GPL"

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Unicode
from sqlalchemy import Sequence
from sqlalchemy import Table
from sqlalchemy.orm import sessionmaker

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, backref

import bcrypt
from datetime import datetime

import types

__all__ = [ 'ThermosBase', 'Permission', 'Group', 'User', 'translations' ]

ThermosBase = declarative_base()

UNUSABLE_PASSWORD = '!'

translations = { 'user_name': 'username', 'group_name': 'name', 'validate_password': 'check_password', 'permission_name': 'name' }

class Permission(ThermosBase):
    """This model represents permissions within the Thermos authentication 
    system. name is required, everything else is optional.
    """
    __tablename__ = 'permissions'

    id = Column(Integer, Sequence('permission_id_seq'), primary_key=True)
    name = Column(Unicode(80), unique=True)
    description = Column(Unicode(255), unique=True)

    def __init__(self, name):
        self.name = name
        self.description = u''

    def __repr__(self):
        return "<Permission('%s')>" % (self.name)

group_permissions = Table('group_permissions', ThermosBase.metadata,
    Column('group_id', Integer, ForeignKey('groups.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class Group(ThermosBase):
    """This model represents groups within the Thermos authentication system.
    name is required, everything else is optional.
    """
    __tablename__ = 'groups'

    id = Column(Integer, Sequence('group_id_seq'), primary_key=True)
    name = Column(Unicode(80), unique=True)
    display_name = Column(Unicode(255), unique=True)
    permissions = relationship('Permission', secondary=group_permissions, backref='groups')

    def __init__(self, name):
        self.name = name
        self.display_name = u''

    def __repr__(self):
        return "<Group('%s')>" % (self.name)

user_groups = Table('user_groups', ThermosBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('group_id', Integer, ForeignKey('groups.id'))
)

user_permissions = Table('user_permissions', ThermosBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)
    
class User(ThermosBase):
    """This model represents users within the Thermos authentication system.
    username is required, everything else is optional.
    """
    __tablename__ = 'users'

    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(Unicode(20), unique=True)
    fullname = Column(Unicode(255))
    password = Column(String(128))
    email = Column(Unicode(255))
    is_active = Column(Boolean)
    created = Column(DateTime, default=datetime.now)
    groups = relationship('Group', secondary=user_groups, backref='users')
    permissions = relationship('Permission', secondary=user_permissions, backref='users')

    def __init__(self, username):
        self.username = username
        self.password = UNUSABLE_PASSWORD
        self.email = u''
        self.fullname = u''
        self.is_active = True

    def __repr__(self):
        return "<User('%s')>" % (self.username)

    def set_password(self, password):
        "Set a password for this user"
        salt = bcrypt.gensalt(log_rounds=12)
        self.password = bcrypt.hashpw(password,salt)

    def check_password(self, raw_password):
        "Validate this user's password"
        salt = self.password[0:29]
        return self.password == bcrypt.hashpw(raw_password,salt)

    def set_unusable_password(self):
        """
        Set the user's password hash to a value that will never match a
        real password (used for locking an account)
        """
        self.password = UNUSABLE_PASSWORD

    def has_perm(self, perm):
        """
        Check if user has the given permission perm
        """

        if not self.is_active:
            return False

        for permission in self.permissions:
            if permission == perm:
                return True

        for group in self.groups:
            for permission in group.permissions:
                if permission == perm:
                    return True

        return False

