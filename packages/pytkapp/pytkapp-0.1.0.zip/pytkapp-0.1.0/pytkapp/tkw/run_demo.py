#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" demo for additional tkinter widgets """

# pytkapp.tkw: demo for additional tkinter widgets
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
    from tkinter import Tk, Toplevel, Button, Entry
    from tkinter.constants import NORMAL, NONE, TOP, LEFT, BOTH, YES, BOTTOM
else:
    from Tkinter import Tk, Toplevel, Button, Entry
    from Tkconstants import NORMAL, NONE, TOP, LEFT, BOTH, YES, BOTTOM

# fixme: uncomment this block to run script directly OR set pythonpath for your package
#if __name__ == '__main__':
    #import sys
    #import os.path
    #lv_file = __file__
    #while os.path.split(lv_file)[1] != '':
        #lv_file = os.path.split(lv_file)[0]
        #print('append %s'%lv_file)
        #sys.path.append(lv_file)

from pytkapp.tkw.tkw_routines import READONLY
from pytkapp.tkw.tkw_alistbox import AListBox
from pytkapp.tkw.tkw_mlistbox import MListBox
from pytkapp.tkw.tkw_xscrolledtext import XScrolledText
from pytkapp.tkw.tkw_xtablelist import XTableList, datesort

from pytkapp.pta_routines import get_estr

def run_demos():
    """ some demos """
    
    root = Tk()
    
    # demo: alistbox
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox demo')
        
        lw_demowidget = AListBox(lw_demotop, [10, 20, 30, 50, 60, 80])
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)     
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))
        
        
    # demo: alistbox + combo
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('alistbox+combo demo')
        
        lw_demowidget = AListBox(lw_demotop, [10, 20, 30, 50, 60, 80], style='combobox', values=[99,88,77,66,55])
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)     
    except:
        print('failed to create demo for "alistbox":\n %s' % (get_estr()))
        
    # demo: mlistbox
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('mlistbox demo')
        
        lw_demowidget = MListBox(lw_demotop, [10, 20, 30, 50, 60, 80], selectallbtn=True)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH)     
    except:
        print('failed to create demo for "mlistbox":\n %s' % (get_estr()))
                
    # demo: xscrolledtext
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('xscrolledtext demo')
        lw_demowidget = XScrolledText(lw_demotop, 
                                      defwidth=80, 
                                      defheight=15, 
                                      search=True,
                                      clear=True,
                                      unload=True,
                                      print_=True,
                                      wstate=READONLY,
                                      wrap=NONE)
        lw_demowidget.pack(side=TOP, expand=YES, fill=BOTH) 
        
        lw_udcf = lw_demowidget.get_udcf()
        lw_btn1 = Button(lw_udcf, text="Button1")
        lw_btn1.pack(side=LEFT)
        lw_btn2 = Button(lw_udcf, text="Button2")
        lw_btn2.pack(side=LEFT)        
        lw_btn3 = Button(lw_udcf, text="Button3")
        lw_btn3.pack(side=LEFT)        
        
        for i in range(50):
            lw_demowidget.insert_data('String: %s\n'%(i))
            
        lw_demowidget.set_wstate(NORMAL)
    except:
        print('failed to create demo for "xscrolledtext":\n %s' % (get_estr()))
        
    # demo: xtablelist
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('xtablelist demo')
        lv_coluns = 7
        lt_headers = ()
        for i in range(lv_coluns):
            lt_headers += ( 0, 'Column'+str(i), )
            
        lw_demowidget = XTableList(lw_demotop,
                                   activestyle="none",
                                   background = "white",
                                   columns = lt_headers,
                                   selecttype="row",
                                   selectmode="extended", #single, browse, multiple, extended
                                   stretch = "all",
                                   stripebackground="gray90",
                                   height=15,
                                   width=0,
                                   titlecolumns=2,
                                   # additional
                                   allowkeepsel=True,
                                   allowsearch=True,
                                   allowresize=True,
                                   allowexport=True,
                                   hscroll=True,
                                   vscroll=True
                                   )
        lw_udcf = lw_demowidget.get_udcf()
        lw_btn1 = Button(lw_udcf, text="Button1")
        lw_btn1.pack(side=LEFT)
        lw_btn2 = Button(lw_udcf, text="Button2")
        lw_btn2.pack(side=LEFT)        
        lw_btn3 = Button(lw_udcf, text="Button3")
        lw_btn3.pack(side=LEFT)        
        
        for r in range(30):
            lt_record = ()
            for i in range(lv_coluns):
                if i != lv_coluns-1:
                    lt_record += ( 'R'+str(r)+': Data'+str(i), )
                else:
                    # make last column data as date
                    lt_record += ('01.01.19'+str(r).rjust(2,'0'),)
            lw_demowidget.get_datawidget().insert("end", lt_record)
        
        lw_demowidget.get_datawidget().columnconfigure(lv_coluns-1, sortcommand = datesort)
    
        # hide one column
        lw_demowidget.get_datawidget().columnconfigure(int(lv_coluns/2), hide="yes")
        
        lw_demowidget.pack(side=BOTTOM, expand=YES, fill=BOTH)
                
        def remove_colums():
            lw_demowidget.get_datawidget().delete(0, "end")
            
            res = lw_demowidget.get_datawidget().cget('-columntitles')
            if isinstance(res, tuple):
                lv_len = len(res)
            else:
                lv_len = 0
            if lv_len > 0:
                lw_demowidget.get_datawidget().deletecolumns(0, lv_len-1)
                
            lv_tlsize = lw_demowidget.get_datawidget().size()
            for ri in range(lv_tlsize):
                ll_data = list(lw_demowidget.get_datawidget().rowcget(ri, "-text"))
                print('%d:%s'%(ri, str(ll_data)))
                
        def add_columns():
            lv_coluns = 7
            lt_headers = ()
            for i in range(lv_coluns):
                lt_headers += ( 0, 'Column'+str(i+10), )
            lw_demowidget.get_datawidget().configure( columns=lt_headers )
            
        Entry(lw_demotop).pack(side=LEFT)            
        Button( lw_demotop, text='Remove columns', command=remove_colums).pack(side=LEFT)        
        Button( lw_demotop, text='Add columns', command=add_columns).pack(side=LEFT)        
    except:
        print('failed to create demo for "xtablelist":\n %s' % (get_estr()))
            
    # show demos
    root.mainloop()

if __name__ == '__main__':    
    run_demos()
