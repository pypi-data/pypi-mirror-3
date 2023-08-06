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
``rattail.db`` -- Database Stuff
"""

from edbob.db.extensions import activate_extension

import rattail


def init_database(engine, session):
    """
    Initialize an ``edbob`` database for use with Rattail.
    """

    activate_extension('rattail', engine)

    columns = [
        ('F01',         'UPC',                  'GPC(14)'),
        ('F02',         'Description',          'CHAR(20)'),
        ('F03',         'Department Number',    'NUMBER(4,0)'),
        ('F22',         'Size',                 'CHAR(30)'),
        ('F155',        'Brand',                'CHAR(30)'),
        ('F238',        'Department Name',      'CHAR(30)'),
        ]

    for name, disp, dtype in columns:
        session.add(rattail.SilColumn(
                sil_name=name, display=disp, data_type=dtype))
        session.flush()

    dictionaries = [
        ('DEPT_DCT', 'Department', [
                ('F03', True),
                'F238',
                ]),
        ('ITEM_DCT', 'Product', [
                ('F01', True),
                'F02',
                'F03',
                'F22',
                'F155',
                ]),
        # ('PRICE_DCT', 'Price', []),
        # ('FCOST_DCT', 'Future Cost', []),
        # ('FSPRICE_DCT', 'Future Sale Price', []),
        # ('CLASS_GROUP', 'Scale Class / Group', []),
        # ('NUTRITION', 'Scale Nutrition', []),
        # ('SCALE_TEXT', 'Scale Text', []),
        # ('VENDOR_DCT', 'Vendor', []),
        ]

    for name, desc, cols in dictionaries:
        bd = rattail.BatchDictionary(name=name, description=desc)
        for col in cols:
            key = False
            if not isinstance(col, basestring):
                col, key = col
            q = session.query(rattail.SilColumn)
            q = q.filter(rattail.SilColumn.sil_name == col)
            col = q.one()
            bd.columns.append(
                rattail.BatchDictionaryColumn(sil_column=col, key=key))
        session.add(bd)
        session.flush()
