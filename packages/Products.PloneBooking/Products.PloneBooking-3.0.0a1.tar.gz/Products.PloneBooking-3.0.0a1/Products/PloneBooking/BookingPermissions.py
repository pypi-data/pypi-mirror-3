# -*- coding: utf-8 -*-
## PloneBooking: Online Booking Tool to allow booking on any kind of ressource
## Copyright (C)2005 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file COPYING. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

"""PloneBooking Permissions"""

__version__ = "$Revision: 1.4 $"
__author__ = ''
__docformat__ = 'restructuredtext'

from Products.CMFCore.permissions import setDefaultRoles

from Products.PloneBooking.config import PLONE_VERSION

# BookingCenter permissions
AddBookingCenter = 'PloneBooking: Add booking center'

# Booking permissions
AddBooking = 'PloneBooking: Add booking'

# Bookable object permissions
AddBookableObject = 'PloneBooking: Add bookable object'

if PLONE_VERSION >= (4, 1):
    mgr_roles = ('Manager', 'Site Administrator')
else:
    mrg_roles = ('Manager',)

# Set up default roles for permissions
setDefaultRoles(AddBookingCenter, mgr_roles + ('Owner', 'Editor'))
setDefaultRoles(AddBooking,
                mgr_roles + ('Owner', 'Member', 'Editor', 'Contributor'))
setDefaultRoles(AddBookableObject, mgr_roles + ('Owner', 'Editor', 'Contributor'))
