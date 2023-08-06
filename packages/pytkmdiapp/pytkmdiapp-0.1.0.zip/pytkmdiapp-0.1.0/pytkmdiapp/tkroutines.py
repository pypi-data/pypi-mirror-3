#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" common routines for tkinter widgets """

# pytkmdiapp - common routines for tkinter widgets
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
import sys

if    sys.hexversion >= 0x03000000:
    from tkinter import Toplevel, TclError, Button, StringVar, Message
else:
    from Tkinter import Toplevel, TclError, Button, StringVar, Message

###################################
## routines
###################################
def tk_focus_get( widget ):
    """ some bug for tablelist """

    name = widget.tk.call('focus')
    if name == 'none' or not name:
        lw_focus = None
    else:
        if name.split('.')[-1] != 'body':
            lv_name = name
        else:
            lv_name = '.'.join(name.split('.')[:-1])

        lw_focus = widget._nametowidget(lv_name)

    return lw_focus

def clipboard_append(event):
    """ add text from called widget to clipboard """

    event.widget.winfo_toplevel().clipboard_clear()
    winfo_class = event.widget.winfo_class()
    if   winfo_class in ['Text','ScrolledText']:
        try:
            lv_frag = event.widget.get('sel.first','sel.last')
            if lv_frag == '':
                lv_frag = event.widget.get('1.0','end')
            event.widget.winfo_toplevel().clipboard_append(lv_frag)
        except TclError:
            event.widget.winfo_toplevel().clipboard_append(event.widget.get('1.0','end'))
    elif winfo_class == 'Entry':
        event.widget.winfo_toplevel().clipboard_append(event.widget.get())

    return "break"

def make_widget_ro( widget):
    """ make widget read-only: accept only Ctrl-C, Ctrl-Ins """

    widget.bind('<Control-KeyPress-c>', clipboard_append)
    widget.bind('<Control-KeyPress-Insert>', clipboard_append)
    widget.bind('<Any-KeyPress>',"break")

def bind_children( widget, event, command, add='+' ):
    """ bind command to all children of widget """

    for child in widget.__dict__['children'].values():
        bind_children(child, event, command, add)

    if hasattr(widget,'body_bind'):
        widget.body_bind(event, command, add)
    widget.bind(event, command, add)

def make_widget_resizeable( widget ):
    """make widget resizeable"""

    cols, rows = widget.grid_size()
    for i in range(0, cols):
        widget.columnconfigure( i, weight=1 )
    for i in range(0, rows):
        widget.rowconfigure( i, weight=1 )

def is_mdichild_subwidget( pw_check ):
    """ check widget - is it mdi child ? """
    lw_master = getattr( pw_check, 'master', None )
    if lw_master is None or lw_master.__class__ in ['Tk','Toplevel']:
        return False
    else:
        if hasattr( lw_master, 'mdichild' ):
            return True
        else:
            return is_mdichild_subwidget( lw_master )

def get_parent_coords( pw_parent ):
    """ get coord of widget parent """

    if isinstance(pw_parent, Toplevel):
        return ( pw_parent.winfo_x(), pw_parent.winfo_y() )
    elif hasattr(pw_parent,'mdichild') or is_mdichild_subwidget( pw_parent ):
        return ( pw_parent.winfo_rootx(), pw_parent.winfo_rooty() )
    else:
        lw_parent = pw_parent.winfo_toplevel()
        return ( lw_parent.winfo_rootx(), lw_parent.winfo_rooty() )

    return (0, 0)

###################################
## classes
###################################
class ToolTippedBtn( Button ):
    """ button with some tooltip """

    def __init__( self, master, **kw ):
        """ init widget """

        self.av_state = 0
        self.hide_afid = None
        self.show_afid = None
        ld_kw = kw

        self.av_tooltip = kw.get('tooltip', '')
        self.aw_showdelay = kw.get('showdelay', 1)
        self.aw_hidedelay = kw.get('hidedelay', 10)

        if 'tooltip' in kw:
            del ld_kw['tooltip']
        if 'showdelay' in kw:
            del ld_kw['showdelay']
        if 'hidedelay' in kw:
            del ld_kw['hidedelay']

        Button.__init__(self, master, **ld_kw)

        self.aw_tooltip_toplevel = Toplevel( master,
                                             bg='black',
                                             padx=1,
                                             pady=1)
        self.aw_tooltip_toplevel.withdraw()
        self.aw_tooltip_toplevel.overrideredirect( True )

        self.av_tooltipvar = StringVar()
        self.av_tooltipvar.set(self.av_tooltip)

        self.aw_tooltip = Message( self.aw_tooltip_toplevel,
                                   bg="#ffffcc",
                                   aspect=1000,
                                   textvariable=self.av_tooltipvar)
        self.aw_tooltip.pack()

        self.bind( '<Enter>', self.init_tooltip, "+" )
        self.bind( '<Leave>', self.hide_tooltip, "+" )

    def init_tooltip( self, event=None ):
        """ check parent activities """

        self.av_state = 1
        self.show_afid = self.after( int( self.aw_showdelay * 1000 ), self.show_tooltip )

    def show_tooltip( self, event=None ):
        """ show tooltip """

        self.av_state = 2
        self.show_afid = None
        # get self position & height
        lv_x = self.winfo_rootx()
        lv_y = self.winfo_rooty()
        lv_height = self.winfo_height()

        # calc coords
        lv_lx = (self.winfo_rootx() + self.aw_tooltip.winfo_width() + 5)
        if lv_lx < self.winfo_screenwidth() - 5:
            lv_x += 5
        else:
            lv_x += self.winfo_screenwidth() - lv_lx

        lv_ly = (self.winfo_rooty() + self.winfo_height() + self.aw_tooltip.winfo_height() + 5)
        if lv_ly < self.winfo_screenheight() - 5:
            lv_y += lv_height + 5
        else:
            lv_y += -(self.aw_tooltip.winfo_height() + 5)

        self.aw_tooltip_toplevel.wm_geometry( "+%d+%d" % ( lv_x, lv_y ) )

        self.aw_tooltip_toplevel.deiconify()
        self.hide_afid = self.after( int( self.aw_hidedelay * 1000 ), self.hide_tooltip )

    def hide_tooltip( self, event=None ):
        """ hide tooltip """

        if self.show_afid is not None:
            self.after_cancel( self.show_afid )
            self.show_afid = None
        if self.hide_afid is not None:
            self.after_cancel( self.hide_afid )
            self.hide_afid = None
        self.av_state = 0
        self.aw_tooltip_toplevel.withdraw()

    def configure( self, **kw ):
        """ configure widget """

        ld_kw = kw

        if 'tooltip' in kw:
            self.av_tooltip = kw.get('tooltip', '')
            self.av_tooltipvar.set(self.av_tooltip)
            del ld_kw['tooltip']
        if 'showdelay' in kw:
            self.aw_showdelay = kw.get('showdelay', 1)
            del ld_kw['showdelay']
        if 'hidedelay' in kw:
            self.aw_hidedelay = kw.get('hidedelay', 10)
            del ld_kw['hidedelay']

        Button.configure(self, **ld_kw)
