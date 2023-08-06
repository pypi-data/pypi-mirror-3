# __init__.py
# Copyright (C) 2012 the CrudAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of CrudAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from colanderalchemy import MappingRegistry
from colanderalchemy import SQLAlchemyMapping
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.expression import and_
from sqlalchemy.sql.expression import or_

__all__ = ['Base']


class Base(object):

    def __init__(self, cls, session=None, create_schema=None,
                 read_schema=None, update_schema=None, delete_schema=None):

        self.cls = cls
        self.session = None
        self.mapping_registry = MappingRegistry(cls)
        if create_schema is None:
            create_schema = SQLAlchemyMapping(cls)

        self.create_schema = create_schema

        if update_schema is None:
            nullables = {name: False
                         for name in self.mapping_registry.pkeys}
            update_schema = SQLAlchemyMapping(cls, nullables=nullables)

        self.update_schema = update_schema

        if read_schema is None:
            nullables = {name: True
                         for name in self.mapping_registry.attrs
                         if name not in self.mapping_registry.pkeys}
            read_schema = SQLAlchemyMapping(cls, nullables=nullables)

        self.read_schema = read_schema

        if delete_schema is None:
            includes = self.mapping_registry.pkeys
            delete_schema = SQLAlchemyMapping(cls, includes=includes)

        self.delete_schema = delete_schema

    def create(self, session=None, **kwargs):

        if session is None:
            session = self.session

        obj = self.cls(**self.create_schema.deserialize(kwargs))
        session.add(obj)

        return obj

    def read(self, session=None, **kwargs):

        if session is None:
            session = self.session

        params = self.read_schema.deserialize(kwargs)

        try:
            id_ = tuple([params[k] for k in self.mapping_registry.pkeys])

        except KeyError as e:
            msg = 'You must specify all primary keys: %s' % e
            raise ValueError(msg)

        obj = session.query(self.cls).get(id_)
        if obj is None:
            msg = '%s %s not found.' % (self.cls.__name__, kwargs)
            raise NoResultFound(msg)

        return obj

    def search(self, session=None, criterions=None, intersect=True,
               order_by=None, start=None, limit=None, raw_query=False):

        if session is None:
            session = self.session

        query = session.query(self.cls)

        if criterions and intersect:
            # Use sqlalchmey AND
            query = query.filter(and_(*criterions))

        elif criterions:
            # Use sqlalchmey OR
            query = query.filter(or_(*criterions))

        if order_by:
            query = query.order_by(*order_by)

        if not raw_query and not start is None and not limit is None:
            end = start + limit
            return query[start:end]

        elif not raw_query and not start is None and limit is None:
            return query[start:]

        elif not raw_query and start is None and not limit is None:
            return query[:limit]

        elif not raw_query and start is None and limit is None:
            return query.all()

        elif raw_query and start is None and limit is None:
            return query

        msg = "'raw_query' and 'start'/'limit' are mutually exclusive."
        raise ValueError(msg)

    def update(self, session=None, **kwargs):

        # NOTE:  update of PKs is not supported.
        # It can be done after using returned obj.
        # NOTE 2: all fields must be provided!

        if session is None:
            session = self.session

        obj = self.cls(**self.update_schema.deserialize(kwargs))
        obj = session.merge(obj)
        if obj in session.new:
            session.expunge(obj)
            msg = "%s %s not found." % (self.cls.__name__, kwargs)
            raise NoResultFound(msg)

        return obj

    def delete(self, session=None, **kwargs):

        if session is None:
            session = self.session

        params = self.delete_schema.deserialize(kwargs)

        try:
            id_ = tuple([params[k] for k in self.mapping_registry.pkeys])

        except KeyError as e:
            msg = 'You must specify all primary keys: %s' % e
            raise ValueError(msg)

        obj = session.query(self.cls).get(id_)
        if obj is None:
            msg = '%s %s not found.' % (self.cls.__name__, kwargs)
            raise NoResultFound(msg)

        session.delete(obj)

        return obj
