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
``rattail.sil`` -- SIL Interface
"""

# from pkg_resources import iter_entry_points

# import rattail
# from rattail.batch import make_batch, RattailBatchTerminal
from rattail.batches import RattailBatchTerminal


# _junctions = None


# class SILError(Exception):
#     """
#     Base class for SIL errors.
#     """

#     pass
    

# class ElementRequiredError(SILError):
#     """
#     Raised when a batch import or export is attempted, but the element list
#     supplied is missing a required element.
#     """

#     def __init__(self, required, using):
#         self.required = required
#         self.using = using

#     def __str__(self):
#         return "The element list supplied is missing required element '%s': %s" % (
#             self.required, self.using)


def default_display(field):
    """
    Returns the default UI display value for a SIL field, according to the
    Rattail field map.
    """

    return RattailBatchTerminal.fieldmap_user[field]


# def get_available_junctions():
#     """
#     Returns a dictionary of available :class:`rattail.BatchJunction` classes,
#     keyed by entry point name.
#     """

#     global _junctions
#     if _junctions is None:
#         _junctions = {}
#         for entry_point in iter_entry_points('rattail.batch_junctions'):
#             _junctions[entry_point.name] = entry_point.load()
#     return _junctions


# def get_junction_display(name):
#     """
#     Returns the ``display`` value for a registered
#     :class:`rattail.BatchJunction` class, given its ``name``.
#     """

#     juncs = get_available_junctions()
#     if name in juncs:
#         return juncs[name].display
#     return None
