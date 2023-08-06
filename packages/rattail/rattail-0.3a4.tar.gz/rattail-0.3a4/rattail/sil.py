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
``rattail.sil`` -- Standard Interchange Language

Please see the `Standard Interchange Language Specifications
<http://productcatalog.gs1us.org/Store/tabid/86/CategoryID/21/List/1/catpageindex/2/Level/a/ProductID/46/Default.aspx>`_
for more information.
"""

import datetime
from decimal import Decimal

import edbob

import rattail


def val(value):
    """
    Returns a string version of ``value``, suitable for inclusion within a data
    row of a SIL batch.  The conversion is done as follows:

    If ``value`` is ``None``, an empty string is returned.

    If it is an ``int`` or ``decimal.Decimal`` instance, it is converted
    directly to a string (i.e. not quoted).

    If it is a ``datetime.date`` instance, it will be formatted as ``'%Y%j'``.

    If it is a ``datetime.time`` instance, it will be formatted as ``'%H%M'``.

    Otherwise, it is converted to a string if necessary, and quoted with
    apostrophes escaped.
    """

    if value is None:
        return ''
    if isinstance(value, int):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime.date):
        return value.strftime('%Y%j')
    if isinstance(value, datetime.time):
        return value.strftime('%H%M')
    if not isinstance(value, basestring):
        value = str(value)
    return "'%s'" % value.replace("'", "''")


def consume_batch_id():
    """
    Returns the next available batch identifier, incrementing the number to
    preserve uniqueness.
    """

    config = edbob.AppConfigParser('rattail')
    config_path = config.get_user_file('rattail.conf', create=True)
    config.read(config_path)

    batch_id = config.get('rattail.sil', 'next_batch_id', default='')
    if not batch_id.isdigit():
        batch_id = '1'
    batch_id = int(batch_id)

    config.set('rattail.sil', 'next_batch_id', str(batch_id + 1))
    config_file = open(config_path, 'w')
    config.write(config_file)
    config_file.close()
    return '%08u' % batch_id


def write_batch_header(fileobj, H03='RATAIL', **kwargs):
    """
    Writes a SIL batch header string to ``fileobj``.  All keyword arguments
    correspond to the SIL specification for the Batch Header Dictionary.

    If you do not override ``H03`` (Source Identifier), then Rattail will
    provide a default value for ``H20`` (Software Revision) - that is, unless
    you've supplied it yourself.

    **Batch Header Dictionary:**

    ====  ====    ====  ===========
    Name  Type    Size  Description
    ====  ====    ====  ===========
    H01   CHAR       2  Batch Type
    H02   CHAR       8  Batch Identifier
    H03   CHAR       6  Source Identifier
    H04   CHAR       6  Destination Identifier
    H05   CHAR      12  Audit File Name
    H06   CHAR      12  Response File Name
    H07   DATE       7  Origin Date
    H08   TIME       4  Origin Time
    H09   DATE       7  Execution (Apply) Date
    H10   DATE       4  Execution (Apply) Time
    H11   DATE       7  Purge Date
    H12   CHAR       6  Action Type
    H13   CHAR      50  Batch Description
    H14   CHAR      30  User Defined
    H15   CHAR      30  User Defined
    H16   CHAR      30  User Defined
    H17   NUMBER     1  Warning Level
    H18   NUMBER     5  Maximum Error Count
    H19   CHAR       7  SIL Level/Revision
    H20   CHAR       4  Software Revision
    H21   CHAR      50  Primary Key
    H22   CHAR     512  System Specific Command
    H23   CHAR       8  Dictionary Revision

    Consult the SIL Specification for more information.
    """

    kw = kwargs

    # Provide default for H20 if batch origin is 'RATAIL'.
    H20 = kw.get('H20')
    if H03 == 'RATAIL' and H20 is None:
        H20 = rattail.__version__[:4]

    # Don't quote H09 if special "immediate" value.
    H09 = kw.get('H09')
    if H09 != '0000000':
        H09 = val(H09)

    # Don't quote H10 if special "immediate" value.
    H10 = kw.get('H10')
    if H10 != '0000':
        H10 = val(H10)
    
    row = [
        val(kw.get('H01')),
        val(kw.get('H02')),
        val(H03),
        val(kw.get('H04')),
        val(kw.get('H05')),
        val(kw.get('H06')),
        val(kw.get('H07')),
        val(kw.get('H08')),
        H09,
        H10,
        val(kw.get('H11')),
        val(kw.get('H12')),
        val(kw.get('H13')),
        val(kw.get('H14')),
        val(kw.get('H15')),
        val(kw.get('H16')),
        val(kw.get('H17')),
        val(kw.get('H18')),
        val(kw.get('H19')),
        val(H20),
        val(kw.get('H21')),
        val(kw.get('H22')),
        val(kw.get('H23')),
        ]
        
    fileobj.write('INSERT INTO HEADER_DCT VALUES\n')
    write_row(fileobj, row, quote=False, last=True)
    fileobj.write('\n')


def write_row(fileobj, row, quote=True, last=False):
    """
    Writes a SIL row string to ``fileobj``.

    ``row`` should be a sequence of values.

    If ``quote`` is ``True``, each value in ``row`` will be ran through the
    :func:`val()` function before being written.  If it is ``False``, the
    values are written as-is.

    If ``last`` is ``True``, then ``';'`` will be used as the statement
    terminator; otherwise ``','`` is used.
    """

    terminator = ';' if last else ','
    if quote:
        row = [val(x) for x in row]
    fileobj.write('(' + ','.join(row) + ')' + terminator + '\n')


def write_rows(fileobj, rows):
    """
    Writes a set of SIL row strings to ``fileobj``.

    ``rows`` should be a sequence of sequences, each of which should be
    suitable for use with :func:`write_row()`.

    (This funcion primarily exists to handle the mundane task of setting the
    ``last`` flag when calling :func:`write_row()`.)
    """

    last = len(rows) - 1
    for i, row in enumerate(rows):
        write_row(fileobj, row, last=i == last)


# # from pkg_resources import iter_entry_points

# # import rattail
# # from rattail.batch import make_batch, RattailBatchTerminal
# from rattail.batches import RattailBatchTerminal


# # _junctions = None


# # class SILError(Exception):
# #     """
# #     Base class for SIL errors.
# #     """

# #     pass
    

# # class ElementRequiredError(SILError):
# #     """
# #     Raised when a batch import or export is attempted, but the element list
# #     supplied is missing a required element.
# #     """

# #     def __init__(self, required, using):
# #         self.required = required
# #         self.using = using

# #     def __str__(self):
# #         return "The element list supplied is missing required element '%s': %s" % (
# #             self.required, self.using)


# def default_display(field):
#     """
#     Returns the default UI display value for a SIL field, according to the
#     Rattail field map.
#     """

#     return RattailBatchTerminal.fieldmap_user[field]


# # def get_available_junctions():
# #     """
# #     Returns a dictionary of available :class:`rattail.BatchJunction` classes,
# #     keyed by entry point name.
# #     """

# #     global _junctions
# #     if _junctions is None:
# #         _junctions = {}
# #         for entry_point in iter_entry_points('rattail.batch_junctions'):
# #             _junctions[entry_point.name] = entry_point.load()
# #     return _junctions


# # def get_junction_display(name):
# #     """
# #     Returns the ``display`` value for a registered
# #     :class:`rattail.BatchJunction` class, given its ``name``.
# #     """

# #     juncs = get_available_junctions()
# #     if name in juncs:
# #         return juncs[name].display
# #     return None
