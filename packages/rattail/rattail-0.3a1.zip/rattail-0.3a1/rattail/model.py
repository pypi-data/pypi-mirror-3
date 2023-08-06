#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
``rattail.db.extension.model`` -- Schema Definition
"""

from __future__ import absolute_import

import re

from sqlalchemy import (Column, String, Integer, Date, DateTime,
                        Boolean, Text, ForeignKey, BigInteger, Numeric)
from sqlalchemy.orm import relationship, object_session

import edbob
from edbob.db.model import Base, uuid_column


__all__ = ['SilColumn', 'BatchDictionaryColumn', 'BatchDictionary',
           'BatchTerminalColumn', 'BatchTerminal', 'BatchColumn',
           'Batch', 'Brand', 'Department', 'Category', 'Product']

sil_type_pattern = re.compile(r'^(CHAR|NUMBER)\((\d+(?:\,\d+)?)\)$')


class SilColumn(Base):
    """
    Represents a SIL-compatible column available to the batch system.
    """

    __tablename__ = 'sil_columns'

    uuid = uuid_column()
    sil_name = Column(String(10))
    display = Column(String(20))
    data_type = Column(String(15))
    
    def __repr__(self):
        return "<SilColumn: %s>" % self.sil_name

    def __str__(self):
        return str(self.sil_name or '')


class BatchDictionaryColumn(Base):
    """
    Represents a column within a :class:`BatchDictionary`.
    """

    __tablename__ = 'batch_dictionary_columns'

    uuid = uuid_column()
    dictionary_uuid = Column(String(32), ForeignKey('batch_dictionaries.uuid'))
    sil_column_uuid = Column(String(32), ForeignKey('sil_columns.uuid'))
    key = Column(Boolean)

    sil_column = relationship(SilColumn)

    def __repr__(self):
        return "<BatchDictionaryColumn: %s>" % self.sil_column

    def __str__(self):
        return str(self.sil_column or '')


class BatchDictionary(Base):
    """
    Represents a SIL-based dictionary supported by one or more
    :class:`BatchTerminal` classes.
    """

    __tablename__ = 'batch_dictionaries'

    uuid = uuid_column()
    name = Column(String(20))
    description = Column(String(255))

    columns = relationship(
        BatchDictionaryColumn,
        backref='dictionary')

    def __repr__(self):
        return "<BatchDictionary: %s>" % self.name

    def __str__(self):
        return str(self.description or '')


class BatchTerminalColumn(Base):
    """
    Represents a column supported by a :class:`BatchTerminal`.
    """

    __tablename__ = 'batch_terminal_columns'

    uuid = uuid_column()
    terminal_uuid = Column(String(32), ForeignKey('batch_terminals.uuid'))
    dictionary_uuid = Column(String(32), ForeignKey('batch_dictionaries.uuid'))
    sil_column_uuid = Column(String(32), ForeignKey('sil_columns.uuid'))
    ordinal = Column(Integer)
    source = Column(Boolean)
    target = Column(Boolean)

    dictionary = relationship(BatchDictionary)
    sil_column = relationship(SilColumn)

    def __repr__(self):
        return "<BatchTerminalColumn: %s, %s, %s>" % (
            self.terminal, self.dictionary, self.sil_column)

    def __str__(self):
        return str(self.sil_column or '')


class BatchTerminal(Base):
    """
    Represents a terminal, or "junction" for batch data.
    """

    __tablename__ = 'batch_terminals'

    uuid = uuid_column()
    sil_id = Column(String(20), unique=True)
    description = Column(String(50))
    class_spec = Column(String(255))
    functional = Column(Boolean, default=False)
    source = Column(Boolean)
    target = Column(Boolean)
    source_kwargs = Column(Text)
    target_kwargs = Column(Text)

    columns = relationship(
        BatchTerminalColumn,
        backref='terminal')

    _terminal = 'not_got_yet'

    def __repr__(self):
        return "<BatchTerminal: %s>" % self.sil_id

    def __str__(self):
        return str(self.description or '')

    def source_columns(self, dictionary):
        for col in self.columns:
            if col.dictionary is dictionary:
                yield col

    def get_terminal(self):
        """
        Returns the :class:`rattail.batches.BatchTerminal` instance which is
        associated with the database record via its ``python_spec`` field.
        """

        if self._terminal == 'not_got_yet':
            self._terminal = None
            if self.class_spec:
                term = edbob.load_spec(self.class_spec)
                if term:
                    self._terminal = term()
        return self._terminal


class BatchColumn(Base):
    """
    Represents a :class:`SilColumn` associated with a :class:`Batch`.
    """

    __tablename__ = 'batch_columns'

    uuid = uuid_column()
    batch_uuid = Column(String(32), ForeignKey('batches.uuid'))
    ordinal = Column(Integer)
    sil_column_uuid = Column(String(32), ForeignKey('sil_columns.uuid'))
    source_uuid = Column(String(32), ForeignKey('batch_terminals.uuid'))
    targeted = Column(Boolean)

    sil_column = relationship(SilColumn)

    source = relationship(
        BatchTerminal,
        primaryjoin=BatchTerminal.uuid == source_uuid,
        order_by=[BatchTerminal.description],
        )

    def __repr__(self):
        return "<BatchColumn: %s, %s>" % (self.batch, self.sil_column)


# def get_sil_column(name):
#     """
#     Returns a ``sqlalchemy.Column`` instance according to Rattail's notion of
#     what each SIL field ought to look like.
#     """

#     type_map = {

#         # The first list of columns is a subset of Level 1 SIL.

#         'F01':
#             Integer,    # upc
#         'F02':
#             String(60), # short (receipt) description
#         'F478':
#             Integer,    # scale text type

#         # The remaining columns are custom to Rattail.

#         'F4001':
#             String(60), # short description, line 2
#         }

#     return Column(name, type_map[name])


def get_sil_type(data_type):
    """
    Returns a SQLAlchemy-based data type according to the SIL-compliant type
    specifier found in ``data_type``.
    """

    if data_type == 'GPC(14)':
        return BigInteger

    m = sil_type_pattern.match(data_type)
    if m:
        data_type, precision = m.groups()
        if precision.isdigit():
            precision = int(precision)
            scale = 0
        else:
            precision, scale = precision.split(',')
            precision = int(precision)
            scale = int(scale)
        if data_type == 'CHAR':
            assert not scale, "FIXME"
            return String(precision)
        if data_type == 'NUMBER':
            return Numeric(precision, scale)

    assert False, "FIXME"
    

class Batch(Base):
    """
    Represents a batch of data, presumably in need of processing.
    """

    __tablename__ = 'batches'

    _rowclass = None
    _row_classes = {}

    uuid = uuid_column()
    source_uuid = Column(String(32), ForeignKey('batch_terminals.uuid'))
    source_description = Column(String(50))
    source_batch_id = Column(String(8))
    batch_id = Column(String(8))
    dictionary_uuid = Column(String(32), ForeignKey('batch_dictionaries.uuid'))
    name = Column(String(30))
    target_uuid = Column(String(32), ForeignKey('batch_terminals.uuid'))
    action_type = Column(String(6))
    elements = Column(String(255))
    description = Column(String(50))
    rowcount = Column(Integer, default=0)
    effective = Column(DateTime)
    deleted = Column(Boolean, default=False)
    sil_type = Column(String(2))
    sil_source_id = Column(String(20))
    sil_target_id = Column(String(20))
    sil_audit_file = Column(String(12))
    sil_response_file = Column(String(12))
    sil_origin_time = Column(DateTime)
    sil_purge_date = Column(Date)
    sil_user1 = Column(String(30))
    sil_user2 = Column(String(30))
    sil_user3 = Column(String(30))
    sil_warning_level = Column(Integer)
    sil_max_errors = Column(Integer)
    sil_level = Column(String(7))
    sil_software_revision = Column(String(4))
    sil_primary_key = Column(String(50))
    sil_sys_command = Column(String(512))
    sil_dict_revision = Column(String(8))
    
    source = relationship(
        BatchTerminal,
        primaryjoin=BatchTerminal.uuid == source_uuid,
        order_by=[BatchTerminal.description],
        )

    dictionary = relationship(
        BatchDictionary,
        order_by=[BatchDictionary.name],
        )

    target = relationship(
        BatchTerminal,
        primaryjoin=BatchTerminal.uuid == target_uuid,
        order_by=[BatchTerminal.description],
        )

    columns = relationship(
        BatchColumn,
        backref='batch',
        )

    # _table = None
    # # _source_junction = 'not set'
    # # _target_junction = 'not set'

    # invalid_name_chars = re.compile(r'[^A-Za-z0-9]')

    def __repr__(self):
        return "<Batch: %s>" % (self.name or '(no name)')

    def __str__(self):
        return str(self.name or '')

    # @property
    # def source_junction(self):
    #     """
    #     Returns the :class:`rattail.BatchJunction` instance associated with
    #     this batch's :attr:`Batch.source` attribute.
    #     """

    #     if self._source_junction == 'not set':
    #         from rattail.sil import get_available_junctions
    #         self._source_junction = None
    #         junctions = get_available_junctions()
    #         if self.source in junctions:
    #             self._source_junction = junctions[self.source]
    #     return self._source_junction

    # @property
    # def table(self):
    #     """
    #     Returns the ``sqlalchemy.Table`` instance for the underlying batch
    #     data.
    #     """

    #     # from sqlalchemy import MetaData, Table, Column, String
    #     from sqlalchemy import Table, Column, String
    #     from rattail import metadata
    #     from rattail.sqlalchemy import get_sil_column

    #     if self._table is None:
    #         # assert self.uuid
    #         assert self.name
    #         name = 'batch.%s.%s' % (self.source, self.batch_id)
    #         if name in metadata.tables:
    #             self._table = metadata.tables[name]
    #         else:
    #             # session = object_session(self)
    #             # metadata = MetaData(session.bind)
    #             columns = [Column('uuid', String(32), primary_key=True, default=get_uuid)]
    #             # columns.extend([get_sil_column(x) for x in self.elements.split(',')])
    #             columns.extend([get_sil_column(x) for x in self.elements.split(',')])
    #             self._table = Table(name, metadata, *columns)
    #     return self._table

    # @property
    # def rowclass(self):
    #     """
    #     Returns a unique subclass of :class:`rattail.BatchRow`, specific to the
    #     batch.
    #     """

    #     if self._rowclass is None:
    #         name = self.invalid_name_chars.sub('_', self.name)
    #         self._rowclass = type('BatchRow_%s' % str(name), (BatchRow,), {})
    #         mapper(self._rowclass, self.table)
    #         # session = object_session(self)
    #         # engine = session.bind
    #         # session.configure(binds={self._rowclass:engine})
    #     return self._rowclass

    @property
    def rowclass(self):
        """
        Returns the SQLAlchemy-mapped class for the underlying data table.
        """

        assert self.uuid
        if self.uuid not in self._row_classes:
            kwargs = {
                '__tablename__':        'batch.%s' % self.name,
                'uuid':                 uuid_column(),
                }
            for col in self.columns:
                kwargs[col.sil_column.sil_name] = Column(get_sil_type(col.sil_column.data_type))
            self._row_classes[self.uuid] = type('BatchRow', (Base,), kwargs)
        return self._row_classes[self.uuid]

    def create_table(self):
        """
        Creates the batch's data table within the database.
        """

        self.rowclass.__table__.create()

    # @property
    # def target_junction(self):
    #     """
    #     Returns the :class:`rattail.BatchJunction` instance associated with
    #     this batch's :attr:`Batch.target` attribute.
    #     """

    #     if self._target_junction == 'not set':
    #         from rattail.sil import get_available_junctions
    #         self._target_junction = None
    #         junctions = get_available_junctions()
    #         if self.target in junctions:
    #             self._target_junction = junctions[self.target]
    #     return self._target_junction

    # def append(self, **row):
    #     """
    #     Appends a row of data to the batch.  Note that this is done
    #     immediately, and not within the context of any transaction.
    #     """

    #     # self.connection.execute(self.table.insert().values(**row))
    #     # self.rowcount += 1
    #     session = object_session(self)
    #     session.add(self.rowclass(**row))
    #     self.rowcount += 1
    #     session.flush()

    def add_rows(self, source, dictionary, **kwargs):
        session = object_session(self)
        source = source.get_terminal()
        for row in source.provide_rows(session, self.rowclass,
                                       dictionary, **kwargs):
            session.add(row)
            session.flush()

    def execute(self):
        """
        Invokes the batch execution logic.  This will instantiate the
        :class:`rattail.batches.BatchTerminal` instance identified by the
        batch's :attr:`target` attribute and ask it to process the batch
        according to its action type.

        .. note::
           No check is performed to verify the current time is appropriate as
           far as the batch's effective date is concerned.  It is assumed that
           other logic has already taken care of that and that yes, in fact it
           *is* time for the batch to be executed.
        """

        target = self.target.get_terminal()
        target.execute_batch(self)

    def provide_rows(self):
        """
        Generator which yields :class:`BatchRow` instances belonging to the
        batch.
        """

        session = object_session(self)
        for row in session.query(self.rowclass):
            yield row


# class BatchRow(edbob.Object):
#     """
#     Superclass of batch row objects.
#     """

#     def __repr__(self):
#         return "<BatchRow: %s>" % self.key_value


class Brand(Base):
    """
    Represents a brand or similar product line.
    """

    __tablename__ = 'brands'

    uuid = uuid_column()
    name = Column(String(100))

    def __repr__(self):
        return "<Brand: %s>" % self.name

    def __str__(self):
        return str(self.name or '')


class Department(Base):
    """
    Represents an organizational department.
    """

    __tablename__ = 'departments'

    uuid = uuid_column()
    number = Column(Integer)
    name = Column(String(30))

    def __repr__(self):
        return "<Department: %s>" % self.name

    def __str__(self):
        return str(self.name or '')


class Category(Base):
    """
    Represents an organizational category for products.
    """

    __tablename__ = 'categories'

    uuid = uuid_column()
    number = Column(Integer)
    name = Column(String(50))
    department_uuid = Column(String(32), ForeignKey('departments.uuid'))

    department = relationship(Department)

    def __repr__(self):
        return "<Category: %s, %s>" % (self.number, self.name)

    def __str__(self):
        return str(self.name or '')

    def __unicode__(self):
        return unicode(self.name or '')


class Product(Base):
    """
    Represents a product for sale and/or purchase.
    """

    __tablename__ = 'products'

    uuid = uuid_column()
    upc = Column(BigInteger)
    department_uuid = Column(String(32), ForeignKey('departments.uuid'))
    category_uuid = Column(String(32), ForeignKey('categories.uuid'))
    brand_uuid = Column(String(32), ForeignKey('brands.uuid'))
    description = Column(String(60))
    description2 = Column(String(60))
    size = Column(String(30))

    department = relationship(Department)
    category = relationship(Category)
    brand = relationship(Brand)

    def __repr__(self):
        return "<Product: %s>" % self.description

    def __str__(self):
        return str(self.description or '')
