# Copyright (c) 2010-2012 Robin Jarry
#
# This file is part of EVE Corporation Management.
#
# EVE Corporation Management is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# EVE Corporation Management is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# EVE Corporation Management. If not, see <http://www.gnu.org/licenses/>.

__date__ = "2011 9 10"
__author__ = "diabeteman"

from datetime import timedelta

from django.template.defaultfilters import register

from ecm.utils.format import print_time_min, print_date, print_duration, print_integer, print_float

#------------------------------------------------------------------------------
@register.filter(name='ecm_date')
def ecm_date(value):
    try:
        return unicode(print_date(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_datetime')
def ecm_datetime(value):
    try:
        return unicode(print_time_min(value))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_time')
def ecm_time(value):
    try:
        if isinstance(value, timedelta):
            return unicode(print_date(value))
        else:
            return unicode(print_date(timedelta(seconds=value)))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_duration_long')
def ecm_duration_long(value):
    try:
        return unicode(print_duration(value))
    except:
        return unicode(value)


#------------------------------------------------------------------------------
@register.filter(name='ecm_qty_diff')
def qty_diff_format(value):
    try:
        return unicode(print_integer(value, force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_quantity')
def qty_format(value):
    try:
        return unicode(print_integer(value))
    except:
        return unicode(value)


#------------------------------------------------------------------------------
@register.filter(name='ecm_amount')
def amount_format(value):
    try:
        return unicode(print_float(value, force_sign=True))
    except:
        return unicode(value)

#------------------------------------------------------------------------------
@register.filter(name='ecm_price')
def price_format(value):
    try:
        return unicode(print_float(value))
    except:
        return unicode(value)
