#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common routines ( Python 3.x ) """

# pytkmdiapp - common routines ( Python 3.x )
#
# Copyright (c) 2012 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

###################################
## import
###################################
import locale

###################################
## constants
###################################
gv_prefenc = locale.getpreferredencoding()

gf_str_encode = str.encode

long_zero = 0

unicode_type = str

###################################
## routines
###################################
def compare( lhs_arg, rhs_arg ):
    if lhs_arg == rhs_arg: return 0
    if lhs_arg > rhs_arg: return 1
    if lhs_arg < rhs_arg: return -1

def cmp_to_key(mycmp):
    """Convert a cmp= function into a key= function"""
    class K(object):
        def __init__(self, obj, *args):
            self.obj = obj
        def __lt__(self, other):
            return mycmp(self.obj, other.obj) < 0
        def __gt__(self, other):
            return mycmp(self.obj, other.obj) > 0
        def __eq__(self, other):
            return mycmp(self.obj, other.obj) == 0
        def __le__(self, other):
            return mycmp(self.obj, other.obj) <= 0
        def __ge__(self, other):
            return mycmp(self.obj, other.obj) >= 0
        def __ne__(self, other):
            return mycmp(self.obj, other.obj) != 0
        def __hash__(self):
            raise TypeError('hash not implemented')
    return K

def to_long( num ):
    if num is None:
        return None
    else:
        return int(num)

def recode_str2unicode( pv_str, p_enc='utf-8', p_mode='strict' ):
    if gv_prefenc == p_enc:
        return pv_str
    else:
        return gf_str_encode(pv_str,gv_prefenc,p_mode).decode( p_enc )

def tu( p_value, p_enc='utf-8' ):
    lv_value = p_value

    if lv_value is None:
        return ''

    if isinstance( lv_value, bytes):
        return str( lv_value, encoding=p_enc)
    elif isinstance( lv_value, str ):
        return lv_value
    else:
        return str( lv_value )
