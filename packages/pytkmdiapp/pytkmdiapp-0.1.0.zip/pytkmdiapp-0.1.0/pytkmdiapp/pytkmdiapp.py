#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" simple mdi application on tkinter - core classes """

# pytkmdiapp - Python package to develop a simple application with
# multi-window interface using tkinter library.
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
import gettext

if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext

if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Menu, StringVar
    from tkinter import Entry, PhotoImage
    from tkinter import Label, Frame, Button, Toplevel
    from tkinter.constants import N, S, W, E, YES, LEFT, RIGHT, TOP, BOTTOM, BOTH, X, FLAT, RAISED, SUNKEN, END, DISABLED, NORMAL
    import tkinter.messagebox as messagebox
    import tkinter.scrolledtext as scrolledtext
else:
    from Tkinter import Tk, Menu, StringVar
    from Tkinter import Entry, PhotoImage
    from Tkinter import Label, Frame, Button, Toplevel
    from Tkconstants import N, S, W, E, YES, LEFT, RIGHT, TOP, BOTTOM, BOTH, X, FLAT, RAISED, SUNKEN, END, DISABLED, NORMAL
    import tkMessageBox as messagebox
    import ScrolledText as scrolledtext

import pytkmdiicons

from tkroutines import tk_focus_get, make_widget_ro, bind_children, ToolTippedBtn
from routines import get_estr, novl, xprint

###################################
## constants
###################################
CHILD_ACTIVE = 'active'
CHILD_BUSY = 'busy'
CHILD_DISABLED = 'disabled'
gv_max_children = 50

if sys.platform == 'win32':
    gv_v_resize_arrow  = 'sb_v_double_arrow'
    gv_h_resize_arrow  = 'sb_h_double_arrow'
    gv_dl_resize_arrow = 'size_nw_se'
else:
    gv_v_resize_arrow  = 'sb_v_double_arrow'
    gv_h_resize_arrow  = 'sb_h_double_arrow'
    gv_dl_resize_arrow = 'bottom_right_corner'

###################################
## classes
###################################
class cl_MDIChild( Frame ):
    """MDI child"""
    def __init__( self, pw_container, global_app, **kw ):
        """ init mid child """

        self.mdichild = 'X'

        parent_widget = kw.get('parentw', None)
        p_id = kw.get('childid', 'window')
        lv_title = kw.get('title', '')
        p_mw = kw.get('mw', 100)
        p_mh = kw.get('mh', 50)
        pv_icondata = kw.get('icon', pytkmdiicons.gv_child_header_icon)

        self.__help = kw.get('helptext', [])
        self.__translator = kw.get('translator', None)

        Frame.__init__(self, pw_container, relief=RAISED, bd=1, takefocus=1)

        self.__id = p_id
        self.__container = pw_container

        self.__ad_resources = {}
        self.__ad_subchildren = {}

        self.__al_xbinds = []


        self.ao_app = global_app
        self.ao_parent = parent_widget

        self.__state = CHILD_DISABLED

        ts = Frame(self, width=1, relief=RAISED, bd=1, cursor=gv_v_resize_arrow)
        ts.grid(row=0, column=0, columnspan=3, sticky=N+E+W+S)

        ls = Frame(self, width=1, relief=RAISED, bd=1, cursor=gv_h_resize_arrow)
        ls.grid(row=1, column=0, sticky=N+E+W+S)

        bs = Frame(self, width=1, relief=RAISED, bd=1, cursor=gv_v_resize_arrow)
        bs.grid(row=2, column=0, columnspan=2, sticky=N+E+W+S)

        local_frame = Frame( self, relief=RAISED)

        lw_headerbar = Frame(local_frame, relief=RAISED, cursor="fleur", bg="dark blue")
        self.__ad_resources['header_bar'] = lw_headerbar

        lw_headerbar.pack(side=TOP, fill=X)

        self.__titlevar = StringVar()
        self.__titlevar.set(lv_title)
        img = PhotoImage(data=pv_icondata)
        titlelabel = Label(lw_headerbar, textvariable=self.__titlevar, fg="white", bg="dark blue", compound=LEFT, image=img)
        titlelabel.pack(side=LEFT, fill=X)
        titlelabel.img = img
        self.__ad_resources['header_title_label'] = titlelabel

        img = PhotoImage(data=pytkmdiicons.gv_child_header_close)
        b = Button(lw_headerbar, image=img, command=self.close, cursor="arrow", width=12, height=12 )
        b.img = img
        b.pack(side=RIGHT, pady=1, padx=2)
        self.__ad_resources['header_close_btn'] = b

        img = PhotoImage(data=pytkmdiicons.gv_child_header_maximize)
        b = Button(lw_headerbar, image=img, command=self.maximize, cursor="arrow", width=12, height=12 )
        b.img = img
        b.pack(side=RIGHT, pady=1)
        self.__ad_resources['header_wstate_btn'] = b

        if len(self.__help) > 0:
            img = PhotoImage(data=pytkmdiicons.gv_child_header_help)
            b = Button(lw_headerbar, image=img, command=self.show_help, cursor="arrow", width=12, height=12 )
            b.img = img
            b.pack(side=RIGHT, pady=1, padx=2)
            self.__ad_resources['header_help_btn'] = b
        else:
            self.__ad_resources['header_help_btn'] = None

        lw_workspace = Frame(local_frame, width=p_mw, height=p_mh, padx=2, pady=2, relief=SUNKEN, bd=2, takefocus=1)
        lw_workspace.pack(side=TOP, expand=YES, fill=BOTH)
        lw_workspace.columnconfigure( 0, weight=1 )

        self.__workspace = lw_workspace

        local_frame.grid( row=1, column=1, sticky=N+E+W+S )

        rs = Frame(self, width=1, relief=RAISED, bd=1, cursor=gv_h_resize_arrow)
        rs.grid( row=1, column=2, sticky=N+E+W+S )

        se = Frame(self, width=2, height=2, bg="gray30", relief=FLAT, bd=1, cursor=gv_dl_resize_arrow)
        se.grid( row=2, column=2, sticky=N+E+W+S )

        self.rowconfigure( 1, weight=1 )
        self.columnconfigure( 1, weight=1 )

        # binding
        lw_headerbar.bind('<ButtonPress-1>', self.checkup)
        titlelabel.bind('<ButtonPress-1>', self.checkup)

        lw_headerbar.bind('<Double-Button-1>', self.toggle_wstate)
        titlelabel.bind('<Double-Button-1>', self.toggle_wstate)

        lw_headerbar.bind('<B1-Motion>', self.moving)
        titlelabel.bind('<B1-Motion>', self.moving)

        ts.bind('<ButtonPress-1>', self.checkup)
        ls.bind('<ButtonPress-1>', self.checkup)
        bs.bind('<ButtonPress-1>', self.checkup)
        rs.bind('<ButtonPress-1>', self.checkup)

        se.bind('<ButtonPress-1>', self.checkup)

        ts.bind('<B1-Motion>', self.sizing)
        ls.bind('<B1-Motion>', self.sizing)
        bs.bind('<B1-Motion>', self.sizing)
        rs.bind('<B1-Motion>', self.sizing)

        se.bind('<B1-Motion>', self.sizing)

        # keep anchors for child
        self.__anchor_ts = ts
        self.__anchor_ls = ls
        self.__anchor_bs = bs
        self.__anchor_rs = rs
        self.__anchor_se = se

        self.__wstate = 0

        self.__ad_geometry = {}
        self.__ad_geometry['up_x'] = None
        self.__ad_geometry['up_y'] = None
        self.__ad_geometry['min_w'] = p_mw
        self.__ad_geometry['min_h'] = p_mh
        self.__ad_geometry['old_x'] = 0
        self.__ad_geometry['old_y'] = 0
        self.__ad_geometry['old_w'] = p_mw
        self.__ad_geometry['old_h'] = p_mh

    def get_resource_item( self, pv_name ):
        """ get some ctrl item """

        return self.__ad_resources.get( pv_name, None )

    def set_resource_item( self, pv_name, pv_value ):
        """ set some ctrl item """

        self.__ad_resources[ pv_name ] = pv_value

    def show_help( self ):
        """ show help text """

        if self.__state == CHILD_ACTIVE:
            lv_wasactive = True
            self.deactivate()
        else:
            lv_wasactive = False

        top_page = Toplevel( self.__container )
        top_page.withdraw()

        top_page.title(_('Help'))
        top_page.protocol("WM_DELETE_WINDOW", top_page.destroy)

        top_page.transient( self.__container )
        top_page.columnconfigure( 0, weight=1 )

        top_frame = Frame(top_page)
        top_frame.grid(sticky=N+E+W+S)

        text = scrolledtext.ScrolledText( top_frame, bg="white", width=80, height=15, padx=2, pady=2 )
        text.pack(side=TOP, fill=BOTH, expand=YES)

        if self.__translator is not None:
            text.insert(END, '\n'.join([self.__translator.get(s) for s in self.__help]))
        else:
            text.insert(END, '\n'.join([s for s in self.__help]))
        make_widget_ro( text )

        top_page.update_idletasks()
        ws_x = self.winfo_rootx()+50
        ws_y = self.winfo_rooty()+50

        lv_width  = top_page.winfo_reqwidth()
        lv_height = top_page.winfo_reqheight()

        top_page.geometry(str(lv_width)+"x"+str(lv_height)+"+"+str(ws_x)+"+"+str(ws_y))
        top_page.resizable( width = False, height = False )

        top_page.minsize(lv_width, lv_height)

        top_page.deiconify()
        top_page.lift()
        top_page.focus_set()
        top_page.grab_set()

        self.__container.wait_window( top_page )

        if lv_wasactive:
            self.activate()

    def set_header_close_btn_command( self, pf_command ):
        """ recommand close btn """

        self.__ad_resources['header_close_btn'].configure( command = pf_command )

    def get_workspace( self ):
        """ get child own workspace """

        return self.__workspace

    def generate_subchild_id( self, pv_id ):
        """ generate id for subchild """

        return self.__id + ':' + pv_id

    def call_subchild( self, pv_id, pv_name ):
        """ activate subchild """

        if not self.has_subchild( pv_id ):
            self.init_subchild( pv_id, pv_name )
            self.wrap_subchild( pv_id )

        self.show_subchild( pv_id )

    def has_subchild( self, pv_id ):
        """ check whether exists subchild with specified id """

        lv_subchildid = self.generate_subchild_id( pv_id )
        return lv_subchildid in self.__ad_subchildren

    def init_subchild( self, pv_id, pv_name ):
        """ initialize subchild """

        lv_subchildid = self.generate_subchild_id( pv_id )

        lo_child = self.ao_app.add_subchild( lv_subchildid, pv_name, self )
        self.__ad_subchildren[ lv_subchildid ] = lo_child

        return lo_child

    def wrap_subchild( self, pv_id ):
        """ place and bind subchild """

        lv_subchildid = self.generate_subchild_id( pv_id )
        lo_child = self.__ad_subchildren[ lv_subchildid ]

        lo_child.propagate()
        self.ao_app.bind_child_onActivate(lo_child, lv_subchildid)

        lv_x = self.winfo_x()
        lv_y = self.winfo_y()
        lo_child.place(x=lv_x+50, y=lv_y+50)

    def activate_subchild( self, pv_id ):
        """ activate specified sub-child """

        if pv_id in self.__ad_subchildren:
            self.__ad_subchildren[ pv_id ].activate()

    def show_subchild( self, pv_id ):
        """ show subchild througout application """

        lv_subchildid = self.generate_subchild_id( pv_id )

        self.ao_app.look_at_child(lv_subchildid, 'show_sub')

    def get_subchildren_ids( self ):
        """ get list of sub-children identifiers """

        return list( self.__ad_subchildren.keys() )

    def close_subchild( self, pv_subchildid ):
        """ close subchild """

        lo_child = self.__ad_subchildren[ pv_subchildid ]

        lo_child.close()
        del self.__ad_subchildren[ pv_subchildid ]

    def close( self ):
        """ close child itself and it sub-children """

        ll_children = self.__ad_subchildren.keys()
        for child in ll_children:
            if hasattr(self.__ad_subchildren[child], 'close'):
                self.__ad_subchildren[child].close()

            del self.__ad_subchildren[child]

        self.destroy()

    def toggle_wstate(self, event):
        """ toggle state of child window """

        if self.__wstate == 0:
            self.maximize()
        else:
            self.restore()

    def fill_wp(self):
        """ fill child workspace """

        # controls >>>
        f = Frame( self.__workspace )

        lw_entry = Entry( f, width=40 )
        lw_entry.pack(side=LEFT, expand=YES, fill=X)

        b1 = Button( f, text='set as name',
                     command=lambda x=1: self.ao_app.configure_wmenu_item( self.__id, 'rename', label=lw_entry.get()) )
        b1.pack(side=LEFT, padx=2)

        b2 = Button( f, text='call subchild',
                     command=lambda x=1: self.call_subchild( lw_entry.get(), 'sub-child ('+lw_entry.get()+')') )
        b2.pack(side=LEFT, padx=2)

        f.pack(side=TOP, fill=X, pady=2)

        # data >>>
        w = scrolledtext.ScrolledText( self.__workspace, bg="white", width=60, height=15, padx=2, pady=2 )
        w.pack(side=TOP, expand=YES, fill=BOTH)

        for i in range(50):
            w.insert(END, 'String: '+str(i)+'\n')

        self.propagate()

    def propagate(self):
        """ save child dimensions and propagate it """

        self.measure_itself()
        self.configure( width=self.__ad_geometry['min_w'], height=self.__ad_geometry['min_h'] )
        self.update_idletasks()
        self.grid_propagate(0)

    def xbind(self, event, command):
        """ bind child and store command for future re-bind """

        bind_children( self, event, command )

        self.__al_xbinds.append( (event, command) )

    def activate(self, p_prev=None):
        """ activate child """

        if self.__state != CHILD_BUSY:
            try:
                if self.__state != CHILD_ACTIVE:

                    self.__state = CHILD_BUSY

                    if p_prev is None:
                        self.lift()
                    else:
                        self.lift( p_prev )

                    self.__ad_resources['header_bar'].configure( bg="dark blue" )
                    self.__ad_resources['header_title_label'].configure( bg="dark blue", fg="white" )

                    # change focus to activated child
                    self.focus_set()
                    self.update_idletasks()

                    self.__state = CHILD_ACTIVE
            except:
                lv_message = '[ERROR] activate child: '+get_estr()
                xprint(lv_message)

    def deactivate(self, p_next=None):
        """ deactivate child """

        if self.__state != CHILD_BUSY:
            try:
                if self.__state != CHILD_DISABLED:

                    self.__state = CHILD_BUSY

                    if p_next is not None:
                        self.lower( p_next )

                    self.__ad_resources['header_bar'].configure( bg="gray75" )
                    self.__ad_resources['header_title_label'].configure( bg="gray75", fg="black" )

                    # release child
                    try:
                        lw_tp = self.winfo_toplevel()
                        lw_f = tk_focus_get( lw_tp )
                        lw_f.grab_release()
                    except:
                        xprint( get_estr() )
                    self.update_idletasks()

                    self.__state = CHILD_DISABLED
            except:
                lv_message = '[ERROR] deactivate child: '+get_estr()
                xprint(lv_message)

    def checkup(self, event):
        """ save child geometry ( coords ) """

        if self.__wstate == 0:
            self.__ad_geometry['up_x'] = self.winfo_pointerx()
            self.__ad_geometry['up_y'] = self.winfo_pointery()

            self.__ad_geometry['old_x'] = self.winfo_x()
            self.__ad_geometry['old_y'] = self.winfo_y()

            self.__ad_geometry['old_w'] = self.winfo_width()
            self.__ad_geometry['old_h'] = self.winfo_height()

    def get_id(self):
        """ return child id """

        return self.__id

    def get_state( self ):
        """ get state of child """

        return self.__state

    def get_wstate( self ):
        """ get state of child window """

        return self.__wstate

    def get_title(self):
        """ return child title """

        return self.__titlevar.get()

    def set_title(self, lv_title):
        """ change child title """

        self.__titlevar.set(lv_title)

    def sizing(self, event):
        """ process child resising """

        try:
            if self.__wstate == 0:
                # determ. direction
                if event.widget == self.__anchor_ls:
                    move_h = True
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_rs:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = False
                elif event.widget == self.__anchor_ts:
                    move_h = False
                    move_v = True
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_bs:
                    move_h = False
                    move_v = False
                    size_h = False
                    size_v = True
                elif event.widget == self.__anchor_se:
                    move_h = False
                    move_v = False
                    size_h = True
                    size_v = True
                else:
                    return

                lv_swpx = self.winfo_pointerx()
                lv_swpy = self.winfo_pointery()

                sx = lv_swpx - novl(self.__ad_geometry['up_x'], lv_swpx)
                sy = lv_swpy - novl(self.__ad_geometry['up_y'], lv_swpy)

                smh = self.__container.winfo_height()
                smw = self.__container.winfo_width()

                # check bottom-right corner
                lv_maxx = self.__container.winfo_rootx() + smw - 1
                lv_maxy = self.__container.winfo_rooty() + smh - 1

                if move_h:
                    sx *= -1
                if move_v:
                    sy *= -1

                ##################################################
                ## calc horizontal shift
                ##################################################
                # left border
                if event.widget == self.__anchor_ls and event.x_root <= self.__container.winfo_rootx()+1:
                    sx = self.__ad_geometry['old_x']
                # right border
                elif event.widget in [self.__anchor_rs, self.__anchor_se] and event.x_root >= lv_maxx:
                    sx = lv_maxx-self.winfo_rootx()-self.__ad_geometry['old_w']
                # minsize
                elif self.__ad_geometry['old_w'] + sx <= self.__ad_geometry['min_w']:
                    sx = self.__ad_geometry['min_w']-self.__ad_geometry['old_w']
                # check back-sizing
                if event.widget == self.__anchor_ls:
                    if self.winfo_pointerx() >= self.__ad_geometry['up_x'] + self.__ad_geometry['old_w'] - self.__ad_geometry['min_w']:
                        self.directmove( event, -sx, 0 )
                        move_h = False

                ##################################################
                ## calc vertical shift
                ##################################################
                # top border
                if event.widget == self.__anchor_ts and event.y_root <= self.__container.winfo_rooty()+1:
                    sy = self.__ad_geometry['old_y']
                # bottom border
                elif event.widget in [self.__anchor_bs, self.__anchor_se] and event.y_root >= lv_maxy:
                    sy = lv_maxy-self.winfo_rooty()-self.__ad_geometry['old_h']
                # minsize
                elif self.__ad_geometry['old_h'] + sy <= self.__ad_geometry['min_h']:
                    sy = self.__ad_geometry['min_h'] - self.__ad_geometry['old_h']
                # check back-sizing
                if event.widget == self.__anchor_ts:
                    if self.winfo_pointery() >= self.__ad_geometry['up_y'] + self.__ad_geometry['old_h'] - self.__ad_geometry['min_h']:
                        self.directmove( event, -sy, 0 )
                        move_v = False

                ##################################################
                ## sizing
                ##################################################
                if size_h and not size_v:
                    self.configure( width=self.__ad_geometry['old_w']+sx)
                if size_v and not size_h:
                    self.configure( height=self.__ad_geometry['old_h']+sy )
                if size_v and size_h:
                    self.configure( width=self.__ad_geometry['old_w']+sx, height=self.__ad_geometry['old_h']+sy )

                ##################################################
                ## moving
                ##################################################
                self.update_idletasks()
                self.moving(event, move_h, move_v)

        except:
            xprint(get_estr())

    def moving(self, event, p_moveh=True, p_movev=True ):
        """ process child moving """

        try:
            if self.__wstate == 0:

                sx = self.winfo_pointerx() - self.__ad_geometry['up_x']
                sy = self.winfo_pointery() - self.__ad_geometry['up_y']

                if p_moveh:
                    vx = self.__ad_geometry['old_x'] + sx
                else:
                    vx = self.__ad_geometry['old_x']
                if p_movev:
                    vy = self.__ad_geometry['old_y'] + sy
                else:
                    vy = self.__ad_geometry['old_y']

                # check top-left corner
                if event.x_root < self.__container.winfo_rootx()+1 or vx <= 0:
                    vx = 1
                if event.y_root < self.__container.winfo_rooty()+1 or vy <= 0:
                    vy = 1

                sww = self.winfo_width()
                smw = self.__container.winfo_width()

                swh = self.winfo_height()
                smh = self.__container.winfo_height()

                # check bottom-right corner
                lv_maxx = self.__container.winfo_rootx()+smw-1
                lv_maxy = self.__container.winfo_rooty()+smh-1

                if event.x_root > lv_maxx or vx+sww >= smw:
                    vx = smw-sww-1

                if event.y_root > lv_maxy or vy+swh >= smh:
                    vy = smh-swh-1

                if not p_moveh:
                    vx = self.winfo_x()
                if not p_movev:
                    vy = self.winfo_y()

                self.place( x=vx, y=vy )
        except:
            xprint(get_estr())

    def directmove(self, event, p_moveh=0, p_movev=0 ):
        """ move child on specified values from current coords """

        try:
            if self.__wstate == 0:

                vx = self.__ad_geometry['old_x'] + p_moveh
                vy = self.__ad_geometry['old_y'] + p_movev

                self.place( x=vx, y=vy )

        except:
            xprint(get_estr())

    def measure_itself(self):
        """ save child geometry ( dimensions ) """

        self.update_idletasks()

        self.__ad_geometry['min_w'] = max(self.winfo_reqwidth(), self.__ad_geometry['min_w'])
        self.__ad_geometry['min_h'] = max(self.winfo_reqheight(), self.__ad_geometry['min_h'])

    def maximize(self, event=None):
        """ max child window to fill parent workspace """

        try:
            self.__wstate = 1
            self.__ad_geometry['old_x'] = self.winfo_x()
            self.__ad_geometry['old_y'] = self.winfo_y()

            del self.__ad_resources['header_wstate_btn'].img
            img = PhotoImage(data=pytkmdiicons.gv_child_header_restore)
            self.__ad_resources['header_wstate_btn'].configure(image=img, command=self.restore)
            self.__ad_resources['header_wstate_btn'].img = img

            self.lift()
            self.place( x = 1, y = 1, relwidth=1, width=-2, relheight=1, height=-2 )

            # configure cursors
            self.__ad_resources['header_bar'].configure( cursor="arrow" )

            self.__anchor_ts.configure( cursor="arrow" )
            self.__anchor_ls.configure( cursor="arrow" )
            self.__anchor_bs.configure( cursor="arrow" )
            self.__anchor_rs.configure( cursor="arrow" )
            self.__anchor_se.configure( cursor="arrow" )

            self.update_idletasks()
        except:
            lv_message = '[ERROR] maximize child: '+get_estr()
            xprint(lv_message)

    def restore(self, event=None):
        """ restore child window to original dimensions """

        try:
            self.__wstate = 0

            del self.__ad_resources['header_wstate_btn'].img
            img = PhotoImage(data=pytkmdiicons.gv_child_header_maximize)
            self.__ad_resources['header_wstate_btn'].configure(image=img, command=self.maximize)
            self.__ad_resources['header_wstate_btn'].img = img

            self.place_forget()
            self.configure( width=self.__ad_geometry['min_w'], height=self.__ad_geometry['min_h'] )
            self.place( x = self.__ad_geometry['old_x'], y = self.__ad_geometry['old_y'], width=None, height=None )

            # configure cursors
            self.__ad_resources['header_bar'].configure( cursor="fleur" )

            self.__anchor_ts.configure( cursor=gv_v_resize_arrow )
            self.__anchor_ls.configure( cursor=gv_h_resize_arrow )
            self.__anchor_bs.configure( cursor=gv_v_resize_arrow )
            self.__anchor_rs.configure( cursor=gv_h_resize_arrow )
            self.__anchor_se.configure( cursor=gv_dl_resize_arrow )

            self.update_idletasks()
        except:
            lv_message = '[ERROR] restore child: '+get_estr()
            xprint(lv_message)

class cl_BasicSubChild( cl_MDIChild ):
    """ another variant of mdi child """

    def __init__(self, pw_container, global_app, **kw):
        """ initialization of subchild """

        cl_MDIChild.__init__(self, pw_container, global_app,
                             parentw=kw.get( 'parentw', None ),
                             childid=kw.get( 'childid', 'window' ),
                             title=kw.get( 'title', '' ),
                             mw=kw.get( 'mw', 250 ),
                             mh=kw.get( 'mh', 100 ),
                             icon=kw.get( 'icon', pytkmdiicons.gv_subchild_header_icon ) )

    def fill_wp(self):
        """ fill child workspace """

        lw_entry = Entry( self.get_workspace(), width=40 )
        lw_entry.pack( side=LEFT, expand=YES, fill=X )

class cl_MDIApp():
    """Simple MDI application"""

    def __init__(self, p_root, **kw):
        if p_root is None:
            self.__root = Tk()
            self.__root.withdraw()
        else:
            if '__root' not in dir(self):
                self.__root = p_root

        lv_minwidth = kw.get( 'minwidth', 640 )
        lv_minheight = kw.get( 'minheight', 480 )

        self.__aw_active_child = None
        self.__av_numerator = 0

        self.__sb_stringvar1 = StringVar()
        self.__sb_stringvar2 = StringVar()
        self.__sb_stringvar3 = StringVar()

        self.__ad_gui_ess_items = {}
        self.__ad_gui_std_items = {}
        self.__ad_resources = {}

        self.__al_children = []
        self.__ad_children = {}
        self.__ad_id2label = {}
        self.__ad_images = {}

        self.__menu = None
        self.__toolbar = None
        self.__workspace = None
        self.__statusbar = None

        # content >>>
        self.create_menu()
        self.create_toolbar()
        self.create_workspace()
        self.create_statusbar()

        # geometry >>>
        self.__toolbar.pack( side = TOP, fill = X )
        self.__workspace.pack( side=TOP, expand=YES, fill=BOTH )
        self.__statusbar.pack( side=BOTTOM, fill=X )

        self.__root.update_idletasks()
        ws_x = self.__root.winfo_rootx()+50
        ws_y = self.__root.winfo_rooty()+50
        lv_width  = max(self.__root.winfo_reqwidth(), lv_minwidth)
        lv_height = max(self.__root.winfo_reqheight(), lv_minheight)
        self.__root.geometry(str(lv_width)+"x"+str(lv_height)+"+"+str(ws_x)+"+"+str(ws_y))
        self.__root.minsize(lv_width, lv_height)

        self.__root.protocol("WM_DELETE_WINDOW", self.call_quit)
        self.__root.resizable(True, True)

    def get_resource_item( self, pv_name ):
        """ get some ctrl item """

        return self.__ad_resources.get( pv_name, None )

    def set_resource_item( self, pv_name, pv_value ):
        """ set some ctrl item """

        self.__ad_resources[ pv_name ] = pv_value

    def get_gui_std_keys( self ):
        """ return list with std gui keys """

        return list( self.__ad_gui_std_items.keys() )

    def get_gui_std_item( self, pv_name ):
        """ return item for gui items """

        return self.__ad_gui_std_items.get( pv_name, None )

    def set_gui_std_item( self, pv_name, pw_item ):
        """ set std gui items """

        self.__ad_gui_std_items[ pv_name ] = pw_item

    def get_gui_ess_keys( self ):
        """ return list with ess gui keys """

        return list( self.__ad_gui_ess_items.keys() )

    def get_gui_ess_item( self, pv_name ):
        """ return item for gui items """

        return self.__ad_gui_ess_items.get( pv_name, None )

    def set_gui_ess_item( self, pv_name, pw_item ):
        """ set std gui items """

        self.__ad_gui_ess_items[ pv_name ] = pw_item

    def get_menu( self ):
        """ get menu widget """

        return self.__menu

    def get_toolbar( self ):
        """ get toolbar widget """

        return self.__toolbar

    def get_workspace( self ):
        """ get workspace frame """

        return self.__workspace

    def get_statusbar( self ):
        """ get statusbar widget """

        return self.__statusbar

    def set_sb_stringvar( self, pv_index, pv_text ):
        """ set StringVar that displayed in status bar (index in 1,2,3) """

        if   pv_index == 1:
            self.__sb_stringvar1.set( pv_text )
        elif pv_index == 2:
            self.__sb_stringvar2.set( pv_text )
        elif pv_index == 3:
            self.__sb_stringvar3.set( pv_text )

    def close( self ):
        """ close entire app """

        for wid in self.__al_children[:]:
            self.del_child(wid)
        self.__root.quit()
        self.__root.destroy()

    def call_quit(self):
        """ call quit """

        if messagebox.askokcancel(_("Confirm"), _("Do you really wish to quit ?")):
            self.close()
            sys.exit(0)

    def create_menu(self):
        """ create top-level menu """
        self.__menu = Menu(self.__root, relief=RAISED)
        self.__root.config(menu=self.__menu)

        self.fill_menu()

    def add_menu_command(self, p_menu, p_name, p_command, p_state=NORMAL):
        """ add command into app menu """

        ld_menu_draft = self.__ad_resources['menu_draft']

        if p_name in ld_menu_draft:

            lv_image = ld_menu_draft[p_name].get('image', None)

            p_menu.add_command( label=ld_menu_draft[p_name]['label'], command=p_command, state=p_state )
            if lv_image is not None:
                try:
                    img = PhotoImage( data=lv_image )
                except:
                    img = None
                if img is not None:
                    p_menu.entryconfigure(END, compound=LEFT, image=img)
                    self.__ad_images[p_name] = img

    def create_menu_wmenu(self):
        """ create default menu for window management """

        if self.__menu is not None:
            lw_menu = Menu(self.__menu, tearoff=0)
            self.__ad_resources['wmenu'] = lw_menu

            self.__menu.add_cascade(label=self.__ad_resources['menu_draft']['window_menu']['label'], menu=lw_menu)
            self.add_menu_command(lw_menu, 'maximize', self.call_maximize_topchild, DISABLED )
            self.add_menu_command(lw_menu, 'restore', self.call_restore_topchild, DISABLED )
            lw_menu.add_separator()
            self.add_menu_command(lw_menu, 'cascade', self.call_cascade_children, DISABLED )

    def reconf_default_wmenu_controls( self, pv_state=NORMAL ):
        """ reconfigure default menu management controls - menu, toolbar """

        # menu
        lw_wmenu = self.__ad_resources['wmenu']
        for i in range( 5 ):
            if i == 4:
                if pv_state == NORMAL:
                    lw_wmenu.add_separator()
                else:
                    lw_wmenu.delete( i )
            else:
                if lw_wmenu.type( i ) != 'separator':
                    lw_wmenu.entryconfigure( i, state=pv_state )

        # toolbar
        for wname in [ 'wtoolbar_del', 'wtoolbar_cascade' ]:
            lw_wtoolbar_item = self.get_gui_std_item( wname )
            lw_wtoolbar_item.configure( state = pv_state )

    def configure_wmenu_item( self, pv_wid, pv_action, **kw ):
        """ configure item in default window menu """

        lw_wmenu = self.__ad_resources['wmenu']
        lv_wlen = lw_wmenu.index(END)+1
        lv_windex = None
        lv_label = self.__ad_id2label[ pv_wid ]
        for lv_index in range(5, lv_wlen):
            if lw_wmenu.type(lv_index) != 'separator':
                lv_wlabel = lw_wmenu.entrycget(lv_index,'label')
                if lv_wlabel == lv_label:
                    lv_windex = lv_index
                    break
        if lv_windex is not None or pv_action in ['add','addsingle']:
            if pv_action == 'delete':
                lw_wmenu.delete( lv_windex )
            elif pv_action == 'recommand':
                lw_wmenu.entryconfigure( lv_windex,
                                         command = lambda wid=pv_wid:self.look_at_child(wid, 'menu'))
            elif pv_action == 'rename':
                lv_newlabel = kw.get('label','')
                lw_wmenu.entryconfigure( lv_windex,
                                         label = lv_newlabel)
                self.__ad_id2label[ pv_wid ] = lv_newlabel
            elif pv_action == 'add':
                lv_wlabel     = kw.get('wlabel','')
                lv_wmainlabel = kw.get('wmainlabel', _('Main window'))

                lw_submenu = Menu(lw_wmenu, tearoff=0)

                lw_submenu.add_command(label = lv_wmainlabel,
                                       command = lambda ch_id=pv_wid:self.look_at_child(ch_id,'menu'))

                lw_wmenu.add_cascade(label = lv_wlabel,
                                       menu = lw_submenu)
            elif pv_action == 'addsingle':
                lv_wlabel     = kw.get('wlabel','')
                lw_wmenu.add_command(label = lv_wlabel,
                                       command = lambda ch_id=pv_wid:self.look_at_child(ch_id,'menu'))

            elif pv_action == 'add_sub':
                lv_wid    = kw.get('wid','')
                lv_wlabel = kw.get('wlabel','')

                lw_submenupath = lw_wmenu.entrycget( lv_windex, 'menu' )
                lw_submenu = lw_wmenu.children[ lw_submenupath.split('.')[-1] ]

                if lw_submenu.index(END) == 0:
                    lw_submenu.add_separator()

                lw_submenu.add_command( label = lv_wlabel,
                                        command = lambda ch_id=lv_wid:self.look_at_child(ch_id,'submenu'))
            elif pv_action == 'del_sub':
                lv_wid    = kw.get('wid','')

                lw_submenupath = lw_wmenu.entrycget( lv_windex, 'menu' )
                lw_submenu = lw_wmenu.children[ lw_submenupath.split('.')[-1] ]

                # loop at submenu - search id
                lv_sublabel = self.__ad_id2label[ lv_wid ]
                for lv_index in range(lw_submenu.index(END)+1):
                    if lw_submenu.type(lv_index) != 'separator':
                        lv_submlabel = lw_submenu.entrycget(lv_index,'label')
                        if lv_submlabel == lv_sublabel:
                            lw_submenu.delete( lv_index )
                            break
                if lw_submenu.index(END) == 1:
                    lw_submenu.delete( END )

    def create_toolbar(self):
        """ create app toolbar """

        self.__toolbar = Frame(self.__root, relief=RAISED, bd=2)
        self.fill_toolbar()

    def create_toolbar_wbtns(self):
        """ create default toolbar buttons """

        ld_toolbar_draft = self.__ad_resources['toolbar_draft']

        # ins window
        lw_ctrlframe = Frame( self.__toolbar, padx=2, pady=2 )
        self.set_gui_std_item( 'wtoolbar_frame', lw_ctrlframe )

        img = PhotoImage( data=pytkmdiicons.gv_app_toolbar_add )
        item = ToolTippedBtn( lw_ctrlframe, image=img, tooltip=ld_toolbar_draft['new_btn']['label'], command=self.call_add_child)
        item.pack(side=LEFT, padx=3, pady=3)
        item.img = img
        self.set_gui_std_item( 'wtoolbar_ins', item )


        # del window
        img = PhotoImage( data=pytkmdiicons.gv_app_toolbar_del )
        item = ToolTippedBtn( lw_ctrlframe, image=img, tooltip=ld_toolbar_draft['close_btn']['label'], command=self.call_del_topchild, state=DISABLED )
        item.pack(side=LEFT, padx=3, pady=3)
        item.img = img
        self.set_gui_std_item( 'wtoolbar_del', item )

        # cascade window
        img = PhotoImage( data=pytkmdiicons.gv_app_toolbar_cascade )
        item = ToolTippedBtn( lw_ctrlframe, image=img, tooltip=ld_toolbar_draft['cascade_btn']['label'], command=self.call_cascade_children, state=DISABLED )
        item.pack(side=LEFT, padx=3, pady=3)
        item.img = img
        self.set_gui_std_item( 'wtoolbar_cascade', item )

        lw_ctrlframe.pack(side=LEFT)

    def create_workspace(self):
        """ create main workspace """

        self.__workspace = Frame(self.__root, bg="dark gray", relief=SUNKEN)

    def create_statusbar(self):
        """ create status bar and associated variables """

        self.__statusbar = Frame(self.__root, relief=RAISED, bd=2)

        self.set_sb_stringvar( 1, 'sb text 1')
        self.set_sb_stringvar( 2, 'sb text 2')
        self.set_sb_stringvar( 3, 'sb text 3')

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar1)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l1', lw_label )

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar2)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l2', lw_label )

        lw_label = Label(self.__statusbar, textvariable=self.__sb_stringvar3)
        lw_label.pack(side=LEFT)
        self.set_gui_std_item( 'l3', lw_label )

    def call_maximize_topchild(self, event=None):
        """ max active child window """

        if self.__aw_active_child is not None:
            self.__aw_active_child.maximize()

    def call_restore_topchild(self, event=None):
        """ restore active child window """

        if self.__aw_active_child is not None:
            self.__aw_active_child.restore()

    def call_cascade_children(self, event=None):
        """ place children in cascade """

        if self.__aw_active_child is not None:
            children_len = len(self.__al_children)
            if children_len > 0:
                v_maxw_w = -1
                v_maxw_h = -1

                # restore all children
                for i in range( children_len-1, -1, -1 ):
                    child_id = self.__al_children[i]
                    self.__ad_children[child_id].restore()

                    lv_currw_w = self.__ad_children[child_id].winfo_width()
                    lv_currw_h = self.__ad_children[child_id].winfo_height()
                    if lv_currw_w > v_maxw_w:
                        v_maxw_w = lv_currw_w
                    if lv_currw_h > v_maxw_h:
                        v_maxw_h = lv_currw_h

                if children_len > 1:
                    v_divisor = (children_len-1)
                else:
                    v_divisor = 1

                v_xstep = (self.__workspace.winfo_width()-v_maxw_w-1 ) / v_divisor
                v_ystep = (self.__workspace.winfo_height()-v_maxw_h-1 ) / v_divisor

                v_topid = self.__aw_active_child.get_id()

                # prepare list in order: child1 sub1 sub2 child2
                ll_clist = []
                for child_id in self.__al_children:
                    lw_child = self.__ad_children[ child_id ]
                    if lw_child.ao_parent is None:
                        ll_clist.append( child_id )
                        ll_clist += lw_child.get_subchildren_ids()

                for i in range( children_len-1, -1, -1 ):
                    child_id = ll_clist[i]
                    lv_x = 1 + v_xstep * i
                    lv_y = 1 + v_ystep * i
                    if child_id != v_topid:
                        self.__ad_children[child_id].lower()
                    self.__ad_children[child_id].place( x = lv_x, y = lv_y )

                self.__aw_active_child.lift()

    def generate_wmenu_label(self, window_id, window_nick=''):
        """ generate label for label in window menu """

        lv_nick = window_nick
        if novl(lv_nick, '') == '':
            lv_nick = 'empty'
        lv_text = window_id+' ( '+lv_nick+' )'

        return lv_text

    def call_add_child(self, event=None):
        """ call new child addition """
        if len(self.__al_children) >= gv_max_children:
            messagebox.showwarning(_('Warning'), _('Maximum number of children !'))
        else:
            lv_child = self.add_child()
            if lv_child is not None:
                lv_child.place(x=1, y=1)
                self.look_at_child(lv_child.get_id(), 'ins')

    def add_child( self ):
        """ create child and configure window menu """

        lw_child = None

        child_id = 'Window'+str(self.__av_numerator)
        self.__av_numerator += 1

        if len( self.__al_children ) == 0:
            self.reconf_default_wmenu_controls( NORMAL )

        lw_child = self.born_child( child_id )

        lw_child.set_header_close_btn_command( lambda wid=child_id: self.call_del_child(wid) )

        self.__ad_children[child_id] = lw_child
        self.__al_children.append(child_id)

        self.bind_child_onActivate(lw_child, child_id)

        lv_label = self.generate_wmenu_label(child_id,'')
        self.set_id2label( child_id, lv_label )

        # configure wmenu
        self.configure_wmenu_item( child_id, 'add', wlabel=lv_label )

        return lw_child

    def born_child(self, child_id):
        """ child generation """

        lw_child = cl_MDIChild( self.__workspace, self, childid=child_id, title=child_id, helptext=['Demo'] )
        lw_child.fill_wp()

        return lw_child

    def add_subchild( self, pv_id, pv_name, po_parent ):
        """ add some sub child """

        lw_child = cl_BasicSubChild( self.__workspace, self,
                                     parentw = po_parent,
                                     childid = pv_id,
                                     title = pv_name )
        lw_child.fill_wp()

        # recommand close btn
        lw_child.set_header_close_btn_command( lambda wid=pv_id: self.call_del_child(wid) )

        self.__ad_children[pv_id] = lw_child
        self.__al_children.append(pv_id)

        self.set_id2label( pv_id, pv_name )

        # configure wmenu
        self.configure_wmenu_item( po_parent.get_id(), 'add_sub', wid=pv_id, wlabel=pv_name )

        return lw_child

    def set_id2label( self, lv_id, lv_label ):
        """ keep id -> label for window menu """

        self.__ad_id2label[lv_id] = lv_label

    def bind_child_onActivate(self, child, child_id):
        """ default binding on child activation """

        lf_c = lambda event, chid = child_id: self.look_at_child(chid, 'b-1', event)
        child.xbind('<Button-1>', lf_c)

    def del_child(self, p_windowid):
        """ child deletion """

        lw_child = self.__ad_children.get(p_windowid, None)

        if lw_child is not None:
            if lw_child.ao_parent is None:
                # configure menu
                self.configure_wmenu_item( p_windowid, 'delete' )

                # delete all children
                for subs_id in lw_child.get_subchildren_ids():
                    self.del_child( subs_id )

                # destroy child
                lw_child.close()
            else:
                # configure menu
                self.configure_wmenu_item( lw_child.ao_parent.get_id(), 'del_sub', wid=p_windowid )

                lw_child.ao_parent.close_subchild( p_windowid )

            # clear internal data
            del self.__ad_children[p_windowid]
            del self.__al_children[self.__al_children.index(p_windowid)]
            del self.__ad_id2label[p_windowid]

            if len( self.__al_children ) == 0:
                self.reconf_default_wmenu_controls( DISABLED )

    def call_del_child(self, p_windowid):
        """ call child deletion """

        lv_topwid = None
        lv_parent = None
        if self.__aw_active_child is not None:
            lv_topwid = self.__aw_active_child.get_id()
            lv_parent = self.__aw_active_child.ao_parent

        self.del_child( p_windowid )

        if lv_topwid == p_windowid:
            self.__aw_active_child = None

            if lv_parent is None:
                self.look_at_child( None, 'reactivate' )
            else:
                self.look_at_child( lv_parent.get_id(), 'ch2parent' )

    def call_del_topchild(self, event=None):
        """ call active child deletion """

        if self.__aw_active_child is not None:
            child_id = self.__aw_active_child.get_id()
            self.del_child( child_id )

            self.__aw_active_child = None
            self.look_at_child( None, 'reactivate' )

    def direct_activation( self, pv_windowid=None ):
        """ direct activation """

        for lo_child in self.__ad_children.values():
            if lo_child.get_id() != pv_windowid:
                lo_child.deactivate()
                lo_child.activate_subchild( pv_windowid )

    def look_at_child(self, pv_windowid, pv_dtext='', po_event=None):
        """ routine for changing focus between children """

        lv_towdw = None
        try:
            if pv_windowid is not None:
                lv_towdw = self.__ad_children[pv_windowid]
            elif len(self.__al_children) > 0:
                lv_towdw = self.__ad_children[self.__al_children[0]]
            else:
                lv_towdw = None

            if lv_towdw is not None:
                lv_oldtop = None
                if self.__aw_active_child != lv_towdw:
                    lv_oldtop = self.__aw_active_child
                    if lv_oldtop is not None:
                        lv_oldtop.deactivate()
                    else:
                        lv_oldtop = None

                if lv_towdw is not None and lv_towdw.get_state() != CHILD_ACTIVE:
                    lv_towdw.activate( lv_oldtop )

            self.__aw_active_child = lv_towdw

        except:
            lv_message = '[ERROR] look_at_child [%s]: %s'% ( pv_dtext, get_estr() )
            xprint( lv_message )

    def create_toolbar_draft(self):
        """ prepare control data of toolbar items """

        self.__ad_resources['toolbar_draft'] = {}

        self.__ad_resources['toolbar_draft']['new_btn']       = {'label':_("New"),     'type':'button'}
        self.__ad_resources['toolbar_draft']['close_btn']     = {'label':_("Close"),   'type':'button'}
        self.__ad_resources['toolbar_draft']['cascade_btn']   = {'label':_("Cascade"), 'type':'button'}

    def fill_toolbar(self):
        """ toolbar filling """

        self.create_toolbar_draft()

        self.create_toolbar_wbtns()

    def create_menu_draft(self):
        """ prepare control data of menu items """

        # fill menu draft
        self.__ad_resources['menu_draft'] = {}

        self.__ad_resources['menu_draft']['window_menu'] = {'label':_("Window"),   'type':'header'}
        self.__ad_resources['menu_draft']['maximize']    = {'label':_("Maximize"), 'type':'control', 'image':pytkmdiicons.gv_app_toolbar_maximize_child }
        self.__ad_resources['menu_draft']['restore']     = {'label':_("Restore"),  'type':'control', 'image':pytkmdiicons.gv_app_toolbar_restore_child }
        self.__ad_resources['menu_draft']['cascade']     = {'label':_("Cascade"),  'type':'control', 'image':pytkmdiicons.gv_app_toolbar_cascade }

    def fill_menu(self):
        """ menu filling """

        self.create_menu_draft()

        self.create_menu_wmenu()

    def run(self):
        """ run application """

        try:
            self.__root.deiconify()
            self.__root.mainloop()
        except SystemExit as x:
            if repr(x.code) != '0':
                xprint( 'SystemExit: %s'%get_estr() )
        except:
            xprint( _( 'Run: %s'%get_estr() ) )

        xprint(_('Closed ...'))
    ###################################

if __name__ == '__main__':

    lo_app = cl_MDIApp( None, minwidth=640, minheight=480 )
    lo_app.run()
