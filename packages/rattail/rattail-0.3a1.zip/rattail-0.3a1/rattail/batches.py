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
``rattail.batches`` -- Batch Interface
"""

# import logging

from sqlalchemy import and_
from sqlalchemy.orm import object_session

import edbob
from edbob.db import needs_session
from edbob.util import requires_impl

import rattail
# from rattail.db import needs_session
# from rattail.util import get_entry_points, requires_impl


# log = logging.getLogger(__name__)
# # _registered_sources = None


# # def get_registered_sources():
# #     """
# #     Returns the entry point map for registered batch sources.
# #     """

# #     global _registered_sources
# #     if _registered_sources is None:
# #         _registered_sources = get_entry_points('rattail.batch_sources')
# #     return _registered_sources


# # @needs_session
# # def get_sources(session):
# #     """
# #     Returns a dictionary of registered :class:`rattail.BatchSource` classes,
# #     keyed by :attr:`BatchSource.name`.
# #     """

# #     sources = {}
# #     for src in session.query(rattail.BatchSource):
# #         sources[src.name] = src
# #     return sources


class BatchTerminal(edbob.Object):
    """
    Defines the interface for data batch terminals.  Subclass this when
    implementing new data awareness and/or integration with external systems.
    """

    @property
    @requires_impl()
    def name(self):
        pass

    @property
    @requires_impl()
    def display(self):
        pass

    @property
    @requires_impl()
    def fieldmap_internal(self):
        pass

    @property
    @requires_impl()
    def fieldmap_user(self):
        pass

    @requires_impl()
    def provide_rows(self, session, rowclass, dictionary, query=None, **kwargs):
        """
        Generator which yields (new) batch row instances.  This is used to
        populate batches.
        """

        raise NotImplementedError

    # def get_elements(self, elements, fieldmap, *required):
    #     """
    #     Returns the proper element list according to current context.
    #     """

    #     if elements is None:
    #         elements = sorted(fieldmap)
    #     self.require_elements(elements, *required)
    #     return elements

    # def require_elements(self, using, *required):
    #     """
    #     Officially require one or more elements when processing a batch.
    #     """

    #     for elements in required:
    #         elements = elements.split(',')
    #         for element in elements:    
    #             if element not in using:
    #                 raise sil.ElementRequiredError(element, using)


class RattailBatchTerminal(BatchTerminal):
    """
    Defines the core batch terminal for Rattail.
    """
    
    name = 'rattail'
    description = "Rattail (local)"

    source_columns = {
        'ITEM_DCT': [
            'F01',
            'F02',
            ],
        }

    target_columns = {
        'DEPT_DCT': [
            'F03',
            'F238',
            ],
        'ITEM_DCT': [
            'F01',
            'F02',
            'F03',
            'F22',
            'F155',
            ],
        }

    def provide_rows(self, session, rowclass, dictionary, query=None, **kwargs):

        if dictionary.name == 'DEPT_DCT':
            if not query:
                query = session.query(rattail.Department)
            for dept in query:
                yield rowclass(
                    F03=dept.number,
                    F238=dept.name,
                    )
            return

        elif dictionary.name == 'ITEM_DCT':
            if not query:
                query = session.query(rattail.Product)
            for product in query:
                yield rowclass(
                    F01=int(product.upc),
                    F02=product.description[:20],
                    F155=product.brand.name if product.brand else None,
                    )
            return

        assert False, "FIXME"

    # def import_main_item(self, session, elements=None, progress_factory=None):
    #     """
    #     Create a main item (ITEM_DCT) batch from current Rattail data.
    #     """

    #     elements = self.get_elements(elements, self.fieldname_map_main_item, 'F01')
    #     batch = make_batch(self.name, elements, session,
    #                        description="Main item data from Rattail")

    #     products = session.query(rattail.Product)
    #     prog = None
    #     if progress_factory:
    #         prog = progress_factory("Creating batch", products.count())
    #     for i, prod in enumerate(products, 1):
    #         fields = {}
    #         for name in elements:
    #             fields[name] = row[self.fieldname_map_main_item[name]]
    #         batch.append(**fields)
    #         if prog:
    #             prog.update(i)
    #     if prog:
    #         prog.destroy()

    #     return batch

    def add_departments(self, session, batch):
        for row in batch.provide_rows():
            dept = rattail.Department()
            dept.number = row.F03
            dept.name = row.F238
            session.add(dept)
            session.flush()

    def add_replace_departments(self, session, batch):
        for row in batch.provide_rows():
            q = session.query(rattail.Department)
            q = q.filter_by(number=row.F03)
            if q.count():
                prods = session.query(rattail.Product)
                prods = prods.filter_by(department_uuid=q.first().uuid)
                if prods.count():
                    prods.update(dict(department_uuid=None), synchronize_session='fetch')
                q.delete(synchronize_session=False)

            dept = rattail.Department()
            dept.number = row.F03
            dept.name = row.F238
            session.add(dept)
            session.flush()

    def add_products(self, session, batch):
        q = session.query(rattail.Department)
        depts = {}
        for dept in q:
            depts[dept.number] = dept

        q = session.query(rattail.Brand)
        brands = {}
        for brand in q:
            brands[brand.name] = brand

        for row in batch.provide_rows():
            dept = None
            if row.F03:
                if row.F03 in depts:
                    dept = depts[row.F03]
                else:
                    dept = rattail.Department(number=row.F03)
                    session.add(dept)
                    session.flush()
                    depts[dept.number] = dept

            brand = None
            if row.F155:
                if row.F155 in brands:
                    brand = brands[row.F155]
                else:
                    brand = rattail.Brand(name=row.F155)
                    session.add(brand)
                    session.flush()
                    brands[brand.name] = brand

            prod = rattail.Product()
            prod.upc = row.F01
            prod.description = row.F02
            prod.size = row.F22
            prod.department = dept
            prod.brand = brand
            session.add(prod)
            session.flush()

    def add_replace_products(self, session, batch):
        q = session.query(rattail.Department)
        depts = {}
        for dept in q:
            depts[dept.number] = dept

        q = session.query(rattail.Brand)
        brands = {}
        for brand in q:
            brands[brand.name] = brand

        products = session.query(rattail.Product)
        for row in batch.provide_rows():
            dept = None
            if row.F03:
                if row.F03 in depts:
                    dept = depts[row.F03]
                else:
                    dept = rattail.Department(number=row.F03)
                    session.add(dept)
                    session.flush()
                    depts[dept.number] = dept

            brand = None
            if row.F155:
                if row.F155 in brands:
                    brand = brands[row.F155]
                else:
                    brand = rattail.Brand(name=row.F155)
                    session.add(brand)
                    session.flush()
                    brands[brand.name] = brand

            q = products.filter_by(upc=row.F01)
            if q.count():
                q.delete(synchronize_session=False)

            prod = rattail.Product()
            prod.upc = row.F01
            prod.description = row.F02
            prod.size = row.F22
            prod.department = dept
            prod.brand = brand
            session.add(prod)
            session.flush()

    def change_departments(self, session, batch):
        depts = session.query(rattail.Department)
        for row in batch.provide_rows():
            dept = depts.filter_by(number=row.F03).first()
            if dept:
                dept.name = row.F238
                session.flush()

    def change_products(self, session, batch):
        q = session.query(rattail.Department)
        depts = {}
        for dept in q:
            depts[dept.number] = dept

        products = session.query(rattail.Product)
        for row in batch.provide_rows():
            prod = products.filter_by(upc=row.F01).first()
            if prod:
                dept = None
                if row.F03:
                    if row.F03 in depts:
                        dept = depts[row.F03]
                    else:
                        dept = rattail.Department(number=row.F03)
                        session.add(dept)
                        session.flush()
                        depts[dept.number] = dept
                prod.dept = dept
                prod.size = row.F22
                session.flush()

    def execute_batch(self, batch):
        """
        Executes ``batch``, which should be a :class:`rattail.Batch` instance.
        """

        session = object_session(batch)

        if batch.action_type == rattail.BATCH_ADD:

            if batch.dictionary.name == 'DEPT_DCT':
                self.add_departments(session, batch)
                return
            if batch.dictionary.name == 'ITEM_DCT':
                self.add_products(session, batch)
                return

        if batch.action_type == rattail.BATCH_ADD_REPLACE:
            if batch.dictionary.name == 'DEPT_DCT':
                return self.add_replace_departments(session, batch)
            if batch.dictionary.name == 'ITEM_DCT':
                return self.add_replace_products(session, batch)

        if batch.action_type == rattail.BATCH_CHANGE:

            if batch.dictionary.name == 'DEPT_DCT':
                self.change_departments(session, batch)
                return

            if batch.dictionary.name == 'ITEM_DCT':
                return self.change_products(session, batch)

        if batch.action_type == rattail.BATCH_REMOVE:
            if batch.dictionary.name == 'DEPT_DCT':
                return self.remove_departments(session, batch)
            if batch.dictionary.name == 'ITEM_DCT':
                return self.remove_products(session, batch)

        assert False, "FIXME"

    def remove_departments(self, session, batch):
        depts = session.query(rattail.Department)
        products = session.query(rattail.Product)
        for row in batch.provide_rows():
            dept = depts.filter_by(number=row.F03).first()
            if dept:
                q = products.filter_by(department_uuid=dept.uuid)
                if q.count():
                    q.update({'department_uuid': None}, synchronize_session=False)
                session.delete(dept)
                session.flush()

    def remove_products(self, session, batch):
        products = session.query(rattail.Product)
        for row in batch.provide_rows():
            prod = products.filter_by(upc=row.F01).first()
            if prod:
                session.delete(prod)
                session.flush()


# def make_batch(source, elements, session, batch_id=None, **kwargs):
#     """
#     Create and return a new SIL-based :class:`rattail.Batch` instance.
#     """

#     if not batch_id:
#         batch_id = next_batch_id(source, consume=True)

#     kwargs['source'] = source
#     kwargs['batch_id'] = batch_id
#     kwargs['target'] = target
#     kwargs['elements'] = elements
#     kwargs.setdefault('sil_type', 'HM')
#     kwargs.setdefault('action_type', rattail.BATCH_ADD_REPLACE)
#     kwargs.setdefault('dictionary', rattail.BATCH_MAIN_ITEM)
#     batch = rattail.Batch(**kwargs)

#     session.add(batch)
#     session.flush()
#     batch.table.create()
#     log.info("Created batch table: %s" % batch.table.name)
#     return batch


@needs_session
def next_batch_id(session, source, consume=False):
    """
    Returns the next available batch ID (as an integer) for the given
    ``source`` SIL ID.

    If ``consume`` is ``True``, the "running" ID will be incremented so that
    the next caller will receive a different ID.
    """

    batch_id = edbob.get_setting('batch.next_id.%s' % source,
                                 session=session)
    if batch_id is None or not batch_id.isdigit():
        batch_id = 1
    else:
        batch_id = int(batch_id)

    while True:
        q = session.query(rattail.Batch)
        q = q.join((rattail.BatchTerminal,
                    rattail.BatchTerminal.uuid == rattail.Batch.source_uuid))
        q = q.filter(and_(
                rattail.BatchTerminal.sil_id == source,
                rattail.Batch.batch_id == '%08u' % batch_id,
                ))
        if not q.count():
            break
        batch_id += 1

    if consume:
        edbob.save_setting('batch.next_id.%s' % source, str(batch_id + 1),
                           session=session)
    return batch_id
