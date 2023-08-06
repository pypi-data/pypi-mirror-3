#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common routines """

# pytkmdiapp - common routines
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
import time
import locale
import traceback
import encodings.aliases as en_aliases
import imp
import os

import sys
if sys.hexversion >= 0x03000000:
    from py3routines import *
else:
    from py2routines import *

###################################
## constants
###################################
gv_encin = locale.getpreferredencoding()
if gv_encin not in en_aliases.aliases.values():
    gv_encin = gv_encin.lower()
    if   gv_encin in en_aliases.aliases:
        gv_encin = en_aliases.aliases[gv_encin]
    else:
        gv_encin = gv_encin.replace('-','_')
        if gv_encin in en_aliases.aliases:
            gv_encin = en_aliases.aliases[gv_encin]
gv_encout = 'utf-8'
if gv_encout not in en_aliases.aliases.values():
    gv_encout = gv_encout.lower()
    if   gv_encout in en_aliases.aliases:
        gv_encout = en_aliases.aliases[gv_encout]
    else:
        gv_encout = gv_encout.replace('-','_')
        if gv_encout in en_aliases.aliases:
            gv_encout = en_aliases.aliases[gv_encout]
gv_defenc = gv_encout

gf_str_decode = str.decode

###################################
## routines
###################################
def xprint( lv_str ):
    lv_printed = False
    try:
        print( lv_str )
        lv_printed = True
    except:

        if isinstance( lv_str, unicode_type ):
            try:
                print( lv_str.encode(gv_defenc) )
                lv_printed = True
            except:
                try:
                    print( lv_str.encode(locale.getpreferredencoding()) )
                    lv_printed = True
                except:
                    pass
        else:
            try:
                print( str(lv_str) )
                lv_printed = True
            except:
                try:
                    print( lv_str.decode(locale.getpreferredencoding()) )
                    lv_printed = True
                except:
                    try:
                        print( lv_str.decode(gv_defenc) )
                        lv_printed = True
                    except:
                        pass

    if not lv_printed:
        print('cannot print data with type='+str(lv_str.__class__))

# py2exe.org recipe
def main_is_frozen():
    return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze

def get_currentfolder():
    currentfolder = ''
    if not main_is_frozen():
        try:
            currentfolder = os.path.split(os.path.abspath(__file__))[0]
        except:
            currentfolder = os.path.abspath(sys.path[0])
    else:
        currentfolder = os.path.realpath(os.path.dirname(sys.argv[0]))

    return currentfolder

def get_logtime():
    return time.strftime("%Y.%m.%d %H:%M:%S",time.localtime(time.time()))

def get_strdate():
    return time.strftime("%Y.%m.%d",time.localtime(time.time()))

def get_strtime():
    return time.strftime("%H:%M:%S",time.localtime(time.time()))

def get_strdatetime():
    return time.strftime("%Y.%m.%d %H:%M:%S",time.localtime(time.time()))

def get_strdatetime_rd():
    return time.strftime("%d.%m.%Y %H:%M:%S",time.localtime(time.time()))

def getcrtime():
    return ('%10.2f'%time.time()).replace('.','')

def get_estr():
    lv_out = ''

    etype, evalue = sys.exc_info()[:2]
    try:
        lv_trlines = traceback.format_exc().splitlines()

        lv_out = tu( 'Type = %s\n'%(etype) )
        lv_out += tu( 'Value = %s\nStack = \n'%( recode_str2unicode( str( evalue ), gv_encin ) ) )

        for i in range( 0, len( lv_trlines ) ):
            lv_out = lv_out + recode_str2unicode(lv_trlines[i], gv_encin)+ '\n'
    except:
        try:
            lv_out = str(etype)+':\n'+str(evalue)+':\n'+str(traceback.format_exc().splitlines())
        except:
            lv_out = str(etype)+':\n'+str(evalue)

    return lv_out

def novl( value, default ):
    if value is None:
        return default
    else:
        return value
