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
``rattail.db.extension.enum`` -- Enumerations
"""


BATCH_ADD                       = 'ADD'
BATCH_ADD_REPLACE               = 'ADDRPL'
BATCH_CHANGE                    = 'CHANGE'
BATCH_LOAD                      = 'LOAD'
BATCH_REMOVE                    = 'REMOVE'

BATCH_ACTION_TYPE = {
    BATCH_ADD                   : "Add",
    BATCH_ADD_REPLACE           : "Add/Replace",
    BATCH_CHANGE                : "Change",
    BATCH_LOAD                  : "Load",
    BATCH_REMOVE                : "Remove",
    }


# BATCH_MAIN_ITEM                 = 'ITEM_DCT'

# BATCH_DICTIONARY = {
#     BATCH_MAIN_ITEM             : "Main Item",
#     }


EMPLOYEE_STATUS_CURRENT         = 1
EMPLOYEE_STATUS_FORMER          = 2

EMPLOYEE_STATUS = {
    EMPLOYEE_STATUS_CURRENT     : "current",
    EMPLOYEE_STATUS_FORMER      : "former",
    }


PRICE_TYPE_REGULAR              = 0
PRICE_TYPE_TPR                  = 1
PRICE_TYPE_SALE                 = 2
PRICE_TYPE_MANAGER_SPECIAL      = 3
PRICE_TYPE_ALTERNATE            = 4
PRICE_TYPE_FREQUENT_SHOPPER     = 5
PRICE_TYPE_MFR_SUGGESTED        = 901

PRICE_TYPE = {
    PRICE_TYPE_REGULAR          : "Regular Price",
    PRICE_TYPE_TPR              : "TPR",
    PRICE_TYPE_SALE             : "Sale",
    PRICE_TYPE_MANAGER_SPECIAL  : "Manager Special",
    PRICE_TYPE_ALTERNATE        : "Alternate Price",
    PRICE_TYPE_FREQUENT_SHOPPER : "Frequent Shopper",
    PRICE_TYPE_MFR_SUGGESTED    : "Manufacturer's Suggested",
    }


UNIT_OF_MEASURE_EACH            = '01'
UNIT_OF_MEASURE_POUND           = '49'

UNIT_OF_MEASURE = {
    UNIT_OF_MEASURE_EACH        : "Each",
    UNIT_OF_MEASURE_POUND       : "Pound",
    }


# VENDOR_CATALOG_NOT_PARSED       = 1
# VENDOR_CATALOG_PARSED           = 2
# VENDOR_CATALOG_COGNIZED         = 3
# VENDOR_CATALOG_PROCESSED        = 4

# VENDOR_CATALOG_STATUS = {
#     VENDOR_CATALOG_NOT_PARSED   : "not parsed",
#     VENDOR_CATALOG_PARSED       : "parsed",
#     VENDOR_CATALOG_COGNIZED     : "cognized",
#     VENDOR_CATALOG_PROCESSED    : "processed",
#     }
