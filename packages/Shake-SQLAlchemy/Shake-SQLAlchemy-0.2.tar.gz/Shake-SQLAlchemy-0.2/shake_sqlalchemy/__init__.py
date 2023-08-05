# -*- coding: utf-8 -*-
"""
    Shake-SQLAlchemy
    ----------------------------------------------

    Implements a basic bridge to SQLAlchemy.

    :Copyright © 2010-2011 by Lúcuma labs (http://lucumalabs.com).
    :MIT License. (http://www.opensource.org/licenses/mit-license.php)

"""
from __future__ import with_statement, absolute_import

import re
from threading import Lock

from shake import json
try:
    import sqlalchemy
except ImportError:
    raise ImportError('Unable to load the sqlalchemy package.'
        ' `Shake-SQLAlchemy` needs the SQLAlchemy library to run.'
        ' You can get download it from http://www.sqlalchemy.org/'
        ' If you\'ve already installed SQLAlchemy, then make sure you have '
        ' it in your PYTHONPATH.')
from sqlalchemy import orm
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import TypeDecorator, Text
from werkzeug.exceptions import NotFound


_CAMELCASE_RE = re.compile(r'([A-Z]+)(?=[a-z0-9])')


class JSONEncodedType(TypeDecorator):
    """Represents an immutable structure as a JSON-encoded string.
    """
    impl = Text

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        return json.loads(value)


def _create_scoped_session(db):
    return scoped_session(sessionmaker(autocommit=False, autoflush=True,
        bind=db.engine))


def _make_table(db):
    def table_maker(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[2:]
        return sqlalchemy.Table(*args, **kwargs)
    return table_maker


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    obj.Table = _make_table(obj)


class _EngineConnector(object):

    def __init__(self, sqlalch):
        self._sqlalch = sqlalch
        self._engine = None
        self._connected_for = None
        self._lock = Lock()

    def get_engine(self):
        with self._lock:
            uri = self._sqlalch.uri
            info = self._sqlalch.info
            options = self._sqlalch.options
            echo = options.get('echo')
            if (uri, echo) == self._connected_for:
                return self._engine
            self._engine = engine = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)
            return engine


class _ModelTableNameDescriptor(object):

    def __get__(self, obj, type):
        tablename = type.__dict__.get('__tablename__')
        if not tablename:
            def _join(match):
                word = match.group()
                if len(word) > 1:
                    return ('_%s_%s' % (word[:-1], word[-1])).lower()
                return '_' + word.lower()
            tablename = _CAMELCASE_RE.sub(_join, type.__name__).lstrip('_')
            setattr(type, '__tablename__', tablename)
        return tablename


class Model(object):
    """Baseclass for custom user models."""

    __tablename__ = _ModelTableNameDescriptor()

    def __repr__(self):
        return '<%s>' % self.__class__.__name__


class SQLAlchemy(object):
    """This class is used to control the SQLAlchemy integration to one
    or more Shake applications.  Depending on how you initialize the
    object it is usable right away or will attach as needed to a
    Shake application.

    There are two usage modes which work very similar.  One is binding
    the instance to a very specific Shake application::

        app = Shake(urls, settings)
        db = SQLAlchemy('sqlite://', app=app)

    The second possibility is to create the object once and configure the
    application later to support it::

        db = SQLAlchemy()

        def create_app():
            app = Shake(urls, settings)
            db.init_app(app)
            return app

    The difference between the two is that in the first case methods like
    :meth:`create_all` and :meth:`drop_all` will work all the time but in
    the second case an app must be running.

    Additionally this class also provides access to all the SQLAlchemy
    functions from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.
    So you can declare models like this::

        class User(db.Model):
            login = db.Column(db.String(80), unique=True)
            passw_hash = db.Column(db.String(80))

    """

    def __init__(self, uri='sqlite://', app=None, echo=False, pool_size=None,
            pool_timeout=None, pool_recycle=None):
        self.uri = uri
        self.info = make_url(uri)

        self.options = self.build_options_dict(echo=echo, pool_size=pool_size,
            pool_timeout=pool_timeout, pool_recycle=pool_recycle)
        self.apply_driver_hacks()
        
        self.connector = None
        self._engine_lock = Lock()
        self.session = _create_scoped_session(self)

        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.db = self
        
        if app is not None:
            self.init_app(app)
        
        _include_sqlalchemy(self)

    def build_options_dict(self, **kwargs):
        options = {'convert_unicode': True}
        for key, value in kwargs.items():
            if value is not None:
                options[key] = value
        return options

    def apply_driver_hacks(self):
        if self.info.drivername == 'mysql':
            self.info.query.setdefault('charset', 'utf8')
            self.options.setdefault('pool_size', 10)
            self.options.setdefault('pool_recycle', 7200)

        elif self.info.drivername == 'sqlite':
            pool_size = self.options.get('pool_size')
            if self.info.database in (None, '', ':memory:'):
                if pool_size == 0:
                    raise RuntimeError('SQLite in-memory database with an '
                        'empty queue (pool_size = 0) is not possible due to '
                        'data loss.')
    
    @property
    def query(self):
        return self.session.query
    
    def add(self, *args, **kwargs):
        return self.session.add(*args, **kwargs)
    
    def commit(self):
        return self.session.commit()
    
    def rollback(self):
        return self.session.rollback()
    
    @property
    def metadata(self):
        """Returns the metadata"""
        return self.Model.metadata

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup.  Never use a database in the context
        of an application not initialized that way or connections will
        leak.
        """
        if self not in app.databases:
            app.databases.append(self)

            @app.before_response
            def shutdown_session(response):
                self.session.remove()
                return response
            
            @app.on_exception
            def rollback(error):
                try:
                    self.session.rollback()
                except (Exception), e:
                    pass

    @property
    def engine(self):
        """Gives access to the engine. """
        with self._engine_lock:
            connector = self.connector
            if connector is None:
                connector = _EngineConnector(self)
                self.connector = connector
            return connector.get_engine()

    def create_all(self):
        """Creates all tables. """
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drops all tables. """
        self.Model.metadata.drop_all(bind=self.engine)

    def reflect(self):
        """Reflects tables from the database. """
        self.Model.metadata.reflect(bind=self.engine)

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, self.uri)

