#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" MListBox - widget based on ListBox with additional
    controls for moving items in list
"""

# pytkapp.tkw: listbox with additional controls (moving)
#
# Copyright (c) 2012 Paul "Mid.Tier"
# Author e-mail: mid.tier@gmail.com

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
    from tkinter import Frame, Listbox, Scrollbar, StringVar
    from tkinter.constants import N, S, W, E
    from tkinter.constants import END, VERTICAL, EXTENDED, NORMAL
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Frame, Listbox, Scrollbar, StringVar
    from Tkconstants import N, S, W, E
    from Tkconstants import END, VERTICAL, EXTENDED, NORMAL
    import tkMessageBox as messagebox
    
# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_routines import toolbar_lbutton_generator
import pytkapp.tkw.tkw_icons as tkw_icons
  
###################################
## classes
################################### 
class MListBox(Frame):
    """ the listbox with an additional controls to reposition items """
    
    def __init__(self, parent, p_list, **kw):
        """ init widget """
        
        Frame.__init__(self, parent)

        self._listvar = StringVar()

        lb_selectallbtn = False
        if 'selectallbtn' in kw:
            lb_selectallbtn = kw['selectallbtn']
            del kw['selectallbtn']
            
        self._listbox = Listbox(self, **kw)
        self._listbox.grid(column=0, row=0, sticky=N+E+W+S, padx=2, pady=2)
        sb = Scrollbar(self)
        sb.config(orient=VERTICAL, command=self._listbox.yview)
        sb.grid(row=0, column=1, sticky=N+S+E)
        self._listbox.config(yscrollcommand=sb.set)
        
        self._listbox.configure( listvariable=self._listvar, activestyle="none", selectmode=EXTENDED )
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        # control frame
        lw_cframe = Frame(self)
        
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Up"), tkw_icons.gv_mlistbox_moveup, NORMAL, self.call_move_up, 2, 2)
        
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Down"), tkw_icons.gv_mlistbox_movedown, NORMAL, self.call_move_down, 2, 2)

        if lb_selectallbtn:
            lw_btn = toolbar_lbutton_generator(lw_cframe, _("Select all"), tkw_icons.gv_mlistbox_selectall, NORMAL, self.call_select_all, 2, 2)
            
        lw_btn = toolbar_lbutton_generator(lw_cframe, _("Reset"), tkw_icons.gv_mlistbox_reset, NORMAL, self.call_reset, 2, 2)
        
        lw_cframe.grid( row=1, column=0, columnspan=2, sticky=N+E+W+S )
        
        self.ab_reordereed = False
        # append initial data
        for item in p_list:
            self._listbox.insert("end", item)
        
        self._list = p_list
   
    def get_selection( self ):
        """ get listbox selection """
        
        return self._listbox.curselection()
    
    def call_select_all( self ):
        """ select all items """
        
        self._listbox.selection_set( 0, "end" )   
    
    def call_move_up(self, event=None):
        """ move item up """
        
        sel = self._listbox.curselection()
        if len(sel) == 1:
            lv_index = int(sel[0])
            lv_newindex = lv_index - 1 
            if lv_newindex >= 0:
                lv_value = self._listbox.get( lv_index )
                # del record
                self._listbox.delete( lv_index )
                # insert record
                self._listbox.insert( lv_newindex, lv_value )
                # select record
                self._listbox.selection_set( lv_newindex )            
                
                self.ab_reordereed = True
        else:
            self._listbox.selection_clear(0, END)
            messagebox.showwarning(_('Caution'), 
                                   _('You need select one record !'),
                                   parent=self.winfo_toplevel())
    
    def call_move_down(self, event=None):
        """ move item down """
        
        sel = self._listbox.curselection()
        if len(sel) == 1:
            lv_index = int(sel[0])
            lv_newindex = lv_index + 1
            if lv_newindex < self._listbox.size():
                lv_value = self._listbox.get( lv_index )
                # del record
                self._listbox.delete( lv_index )
                # insert record
                self._listbox.insert( lv_newindex, lv_value )
                # select record
                self._listbox.selection_set( lv_newindex )  
                
                self.ab_reordereed = True
        else:
            self._listbox.selection_clear(0, END)
            messagebox.showwarning(_('Caution'), 
                                   _('You need select one record !'),
                                   parent=self.winfo_toplevel())
    
    def call_reset(self, event=None):
        """ restore items positions """
        
        self._listbox.selection_clear(0, END)
        self._listbox.delete(0, END)
        for item in self._list:
            self._listbox.insert("end", item)
            
        self.ab_reordereed = False
    
    def get_list(self, event=None):
        """ get widget items as list """
        
        ll_out = []
        for i in range(self._listbox.size()):
            ll_out.append(self._listbox.get( i ))
                          
        return ll_out
   