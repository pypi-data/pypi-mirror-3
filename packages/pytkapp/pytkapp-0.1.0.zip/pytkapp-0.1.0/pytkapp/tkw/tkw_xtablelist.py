#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" tablelist widget with scrolling and additional 
    controls (search, clear, unload, etc.)
"""

# pytkapp.tkw: tablelist widget with scrolling and additional controls
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
import os
import os.path
import codecs
import datetime
import itertools
import gettext
if __name__ == '__main__':
    if    sys.hexversion >= 0x03000000:
        gettext.install(__name__)
    else:
        gettext.install(__name__, unicode=True)
elif '_' not in __builtins__:
    _ = gettext.gettext     

if    sys.hexversion >= 0x03000000:
    from tkinter import Tk, Toplevel, Frame, Scrollbar, StringVar, TclError
    from tkinter.constants import N, S, W, E, X, NE
    from tkinter.constants import NORMAL, LEFT, RIGHT, VERTICAL, HORIZONTAL
    import tkinter.filedialog as filedialog
    import tkinter.messagebox as messagebox
else:
    from Tkinter import Tk, Toplevel, Frame, Scrollbar, StringVar, TclError
    from Tkconstants import N, S, W, E, X, NE
    from Tkconstants import NORMAL, LEFT, RIGHT, VERTICAL, HORIZONTAL
    import tkFileDialog as filedialog
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

from pytkapp.tkw.tablelistwrapper import TableList
from pytkapp.tkw.tkw_searchdialog import SearchDialog
from pytkapp.tkw.tkw_routines import get_estr, toolbar_lbutton_generator, toolbar_separator_generator
import pytkapp.tkw.tkw_icons as tkw_icons

from pytkapp.pta_routines import gv_defenc, tu, convert_fname, novl, xprint

###################################
## globals
###################################  
gl_akw = ['allowsearch',
          'allowresize',
          'allowexport',
          'allowkeepsel',
          'allowtree',
          'exportdir',
          'hscroll',
          'vscroll',
          'presearchcmd',
          'postsearchcmd']

###################################
## routines
###################################  
def datesort( lhs, rhs ):
    """ sort for data in text format """
    
    lv_out = 0

    lv_lhs = lhs
    lv_rhs = rhs

    # short date
    if len(lhs) == 10:
        lv_source = lhs
        if   lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_lhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_lhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    if len(rhs) == 10:
        lv_source = rhs
        if   lv_source.find('.') != -1 and len(lv_source.split('.')) == 3:
            lv_separator = '.'
        elif lv_source.find('-') != -1 and len(lv_source.split('-')) == 3:
            lv_separator = '-'
        elif lv_source.find('/') != -1 and len(lv_source.split('/')) == 3:
            lv_separator = '/'
        else:
            lv_separator = ''

        if lv_separator != '':
            lv_s = lv_source.split(lv_separator)

            if lv_source.find(lv_separator) == 2:
                lv_rhs = datetime.date(int(lv_s[2]), int(lv_s[1]), int(lv_s[0]))
            else:
                lv_rhs = datetime.date(int(lv_s[0]), int(lv_s[1]), int(lv_s[2]))

    lv_out = cmp(lv_lhs, lv_rhs)
    if lv_out not in [0, 1, -1]:
        lv_out = 0

    return lv_out


###################################
## classes
###################################  
class XTableList(Frame):
    """ Tablelist with search and additional controls """
    
    def __init__(self, parent, **kw):
        """ init widget 
        
            kw: contain tablelist-specific keys and some additional:
                allowsearch: True/False - call or not search dialog
                allowresize: True/False - show sizers btns      
                allowtree: True/False - show tree btns
                allowexport: True/False - add btn to export table to csv
                allowkeepsel: True/False - try to keep single selection highlighted ?
                exportdir: default folder for export
                hscroll: True/False - add or not horizontal scrollbar
                vscroll: True/False - add or not vertical scrollbar
                presearchcmd: if not None than this func will be fired before dialog pop-up
                postsearchcmd: if not None than this func will be fired after dialog closing
        """
        Frame.__init__(self, parent)

        self.__datawidget = None
        self.__lastsearch = None
        self.__presearchcmd = None
        self.__postsearchcmd = None
        
        self.__keepsel = None
        self.__keepsel_bg = None
        self.__keepsel_fg = None
        
        self.__colaliases = []
              
        # extract additional keywords          
        lb_allowsearch = kw.get('allowsearch', False)
        lb_allowresize = kw.get('allowresize', False)
        lb_allowexport = kw.get('allowexport', False)
        lb_allowtree   = kw.get('allowtree',   False)
        
        lb_hscroll = kw.get('hscroll', False)
        lb_vscroll = kw.get('vscroll', False)
        self.__exportdir = kw.get('exportdir', os.getcwd())
        self.__presearchcmd = kw.get('presearchcmd', None)
        self.__postsearchcmd = kw.get('postsearchcmd', None)    
        lv_keepsel = kw.get('allowkeepsel', False)
            
        # clear kw
        for akw in gl_akw:
            kw.pop(akw, None)
                    
        self.__datawidget = TableList(self, **kw)
        
        if lv_keepsel:
            self.__datawidget.bind('<<TablelistSelect>>', self.on_get_selection, '+' )
            self.__datawidget.bind('<<TablelistSelectionLost>>', self.on_lose_selection, '+' )
        
        self.__datawidget.grid(row=0, column=0, sticky=N+E+W+S)
        self.__datawidget.configure( labelcommand = self.on_header_click )

        lv_mr = 0

        if lb_vscroll:
            vbar = Scrollbar(self, name='vbar', orient=VERTICAL)
            self.__datawidget['yscrollcommand'] = vbar.set
            vbar['command'] = self.__datawidget.yview
            vbar.grid(row=0, column=1, sticky=N+E+W+S)

        if lb_hscroll:
            lv_mr += 1
            hbar = Scrollbar(self, name='hbar', orient=HORIZONTAL)
            self.__datawidget['xscrollcommand'] = hbar.set
            hbar['command'] = self.__datawidget.xview
            hbar.grid(row=lv_mr, column=0, sticky=N+E+W+S)

        self.columnconfigure( 0, weight=1 )
        self.rowconfigure( 0, weight=1 )

        if lb_allowsearch:
            self.__lastsearch = StringVar()
            self.__datawidget.body_bind('<Control-KeyPress-f>', self.call_seach_dialog)
            self.__datawidget.body_bind('<F3>', lambda event, m='single': self.call_reseach(m))
            self.__datawidget.body_bind('<Control-F3>', lambda event, m='all': self.call_reseach(m))
        
        ## forward the tablelist methods to myself (Frame)
        methods = TableList.__dict__.keys()
        for m in methods:
            if m not in ('curselection', 'getcurselection', 'clear'):
                setattr(self, m, getattr(self.__datawidget, m))

        lv_mr += 1
        lw_bottomframe = Frame(self)
        
        self.__udcf = Frame(lw_bottomframe)
        self.__udcf.pack(side=LEFT, fill=X, padx=1, pady=1) 
        
        if lb_allowresize or lb_allowexport or lb_allowtree:
            lw_cf = Frame(lw_bottomframe)
            
            lv_r = 0
            lv_c = 0
            
            if lb_allowtree:
                item = toolbar_lbutton_generator(lw_cf, _('Collapse'), tkw_icons.gv_icon_tree_collapseall, NORMAL, lambda event=None, f=0: self.call_collapse(f), 2, 2)
                item.bind('<Control-Button-1>', lambda event=None, f=1: self.call_collapse(f))
                
                item = toolbar_lbutton_generator(lw_cf, _('Expand'), tkw_icons.gv_icon_tree_expandall, NORMAL, lambda event=None, f=0: self.call_expand(f), 2, 2)
                item.bind('<Control-Button-1>', lambda event=None, f=1: self.call_expand(f))
                
                if lb_allowresize or lb_allowexport:
                    toolbar_separator_generator(lw_cf, 3)
                
            if lb_allowresize:
                item = toolbar_lbutton_generator(lw_cf, _('Resize by data'), tkw_icons.gv_xtablelist_resizebydata, NORMAL, self.call_resizebydata, 2, 2)
                
                item = toolbar_lbutton_generator(lw_cf, _('Resize by headers'), tkw_icons.gv_xtablelist_resizebyheaders, NORMAL, self.call_resizebyheaders, 2, 2)
                
                if lb_allowexport:
                    toolbar_separator_generator(lw_cf, 3)
                
            if lb_allowexport:
                item = toolbar_lbutton_generator(lw_cf, _('Export data'), tkw_icons.gv_xtablelist_export, NORMAL, self.call_export, 2, 2)
    
            lw_cf.pack(side=RIGHT, anchor=NE, padx=1, pady=1)
            
        lw_bottomframe.grid(row=lv_mr, column=0, columnspan=2, sticky=N+E+W+S, pady=2)
        
    def set_aliases(self, pl_aliases):
        """ set aliases for tablelist """
        
        self.__colaliases = pl_aliases
        
    def get_colindex4alias(self, pv_alias):
        """ get index of column by alias """
        
        for i, data in enumerate(self.__colaliases):
            if data.upper() == pv_alias.upper():
                return i  
            
        raise IndexError
        
    def get_colindex4title(self, pv_title):
        """ get index of column by title """
        
        lv_res = self.__datawidget.cget('-columntitles')
        if isinstance(lv_res, tuple) and len(lv_res) > 0:        
            for i, data in enumerate(lv_res):
                if data.upper() == pv_title.upper():
                    return i  
            
        raise IndexError
            
    def get_udcf(self):
        """ return user-defined control frame """
       
        return self.__udcf
    
    def on_get_selection(self, po_event=None):
        """ process when tablelist select """
        
        if self.__datawidget.cget('-selectmode') in ('single','browse'):
            
            self.restore_keepsel_row()
        
            lv_selection = self.__datawidget.curselection()
            if len(lv_selection) == 1:
                self.__keepsel = lv_selection[0]
                self.__keepsel_bg = self.__datawidget.rowcget(self.__keepsel, '-background')
                self.__keepsel_fg = self.__datawidget.rowcget(self.__keepsel, '-foreground')
                                                
    def get_keepsel(self):
        """ return index of last selected row """
        
        return self.__keepsel
    
    def restore_keepsel_row(self):
        """ restore keepsel row """
        
        if self.__keepsel is not None:
            try:
                self.__datawidget.rowconfigure(self.__keepsel, 
                                               bg=self.__keepsel_bg, 
                                               fg=self.__keepsel_fg)
            except TclError:
                # record may be deleted externaly...
                pass
            
        self.__keepsel = None        
            
    def restore_keepsel_sel(self):
        """ restore selection from keepsel data """
           
        if self.__keepsel is not None and len(self.__datawidget.curselection()) == 0:
            self.__datawidget.selection_set(self.__keepsel)
                                   
    def on_lose_selection(self, po_event=None):
        """ process when losing selection """
        
        if self.__keepsel is not None:
            try:
                self.__datawidget.rowconfigure(self.__keepsel, 
                                               bg=self.__datawidget.cget('-selectbackground'), 
                                               fg=self.__datawidget.cget('-selectforeground'))
            except TclError:
                # record may be deleted externaly...
                pass 
                
    def call_seach_dialog(self, event=None):  
        """ call search dialog for widget """
        
        if self.__presearchcmd is not None:
            self.__presearchcmd()
            
        s = SearchDialog( self,
                          self.__datawidget, 
                          lastsearch=self.__lastsearch,
                          postsearchcmd=self.__postsearchcmd)
        
        lv_index = s.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see( lv_index )
            self.__datawidget.update_idletasks()
            
            return "break"      
        
    def call_reseach(self, pv_mode=None):
        """ process single re-search without pop-up dialog """
        
        if self.__presearchcmd is not None:
            self.__presearchcmd()
            
        s = SearchDialog( self,
                          self.__datawidget, 
                          lastsearch=self.__lastsearch,
                          research=pv_mode,
                          postsearchcmd=self.__postsearchcmd)
        
        lv_index = s.get_firstindex()
        if lv_index is not None:
            self.__datawidget.see( lv_index )
            self.__datawidget.update_idletasks()
            
            return "break"
        
    def getcurselection(self):
        """ override standard getcurselection """
        
        lv_rsel = self.__datawidget.getcurselection()
        if self.__keepsel is not None and len(lv_rsel) == 0:
            lv_outsel = (self.__keepsel, )
        else:
            lv_outsel = lv_rsel
            
        return lv_outsel    
    
    def curselection(self):
        """ override standard curselection """
        
        lv_rsel = self.__datawidget.curselection()
        if self.__keepsel is not None and len(lv_rsel) == 0:
            lv_outsel = (self.__keepsel, )
        else:
            lv_outsel = lv_rsel
            
        return lv_outsel            
        
    def get_datawidget(self):
        """ return datawidget """
        
        return self.__datawidget
    
    def call_collapse(self, force=0):
        """ collapse selected row  or entire tree """
        
        if force == 1:
            self.__datawidget.collapseall()
        else:
            lt_selection = self.curselection()
            if len(lt_selection) == 0:
                self.__datawidget.collapseall()
            else:
                for row_index in lt_selection:
                    self.__datawidget.collapse(row_index)
        
    def call_expand(self, force=0):
        """ expand selected row  or entire tree """
        
        if force == 1:
            self.__datawidget.expandall()
        else:
            lt_selection = self.curselection()
            if len(lt_selection) == 0:
                self.__datawidget.expandall()
            else:
                for row_index in lt_selection:
                    self.__datawidget.expand(row_index)
        
    def call_resizebydata(self, event=None):  
        """ set width of columns by data """
        
        for ci in range(self.__datawidget.columncount()):
            self.__datawidget.columnconfigure(ci, width=0)
        
    def call_resizebyheaders(self, event=None):  
        """ set width of columns by headers """
        
        for ci in range(self.__datawidget.columncount()):
            h_len = len(self.__datawidget.columncget(ci,'-title'))+1
            self.__datawidget.columnconfigure(ci, width=h_len)
            
    def call_export(self, event=None):  
        """ export table to csv-file """
        
        lv_defexportpath = self.__exportdir
        if not os.path.isdir(lv_defexportpath):
            lv_defexportpath = os.getcwd()
            xprint('Warning! Default folder for export doesnt exists: %s'%(self.__exportdir))
            
        lv_exportpath = filedialog.asksaveasfilename(title=_('Export data'), 
                                                     filetypes = {"csv-file {.csv}":0},
                                                     initialdir=lv_defexportpath,
                                                     defaultextension='csv',
                                                     parent=self.__datawidget.winfo_toplevel()\
                                                     )
        lv_exportpath = convert_fname( lv_exportpath )
        
        if novl(lv_exportpath,'') != '':
            lv_exportpath = os.path.realpath(lv_exportpath).lower()
            if os.path.splitext(lv_exportpath.lower())[1] != '.csv':
                lv_exportpath += '.csv'
            lv_folder = os.path.split(lv_exportpath)[0]
            if os.path.exists(lv_folder):
                with codecs.open(lv_exportpath, 'w+', gv_defenc) as lo_f:
                    lv_tlsize = self.__datawidget.size()
                    # save header
                    lt_headers = self.__datawidget.cget('-columntitles')
                                        
                    lo_f.write(tu(';').join([tu(i) for i in lt_headers])+'\n')
                    # save data
                    for ri in range(lv_tlsize):
                        ll_data = list(self.__datawidget.rowcget(ri,"-text"))
                        
                        lo_f.write(tu(';').join([tu(i) for i in ll_data])+'\n')
                        
                messagebox.showinfo(_('Info'), _('Export completed !'), detail=lv_exportpath, parent=self.__datawidget.winfo_toplevel())
                
    def on_header_click( self, pv_tlpath, pv_column ):
        """ process sorting for column """
        
        lv_order = "-increasing"
        if self.__datawidget.sortcolumn() == int(pv_column) and self.__datawidget.sortorder() == "increasing":
            lv_order = "-decreasing"
                        
        self.__datawidget.sortbycolumn(pv_column, lv_order)
        
        if self.__keepsel is not None:
            lv_cursel = self.__datawidget.curselection()
            if len(lv_cursel) == 1:
                lv_cursel_ind = lv_cursel[0]
            else:
                lv_cursel_ind = -1
                
            if lv_cursel_ind != self.__keepsel:
                lv_selbg = self.__datawidget.cget('-selectbackground')
                for i in range(self.__datawidget.size()):
                    if str(self.__datawidget.rowcget(i, '-background')) == lv_selbg:
                        if i != lv_cursel_ind:
                            self.__keepsel = i
                            break
        
    def clear_(self, po_event=None):
        """ clear internal structires """

        self.__keepsel = None
        self.__colaliases = []
        if self.__lastsearch is not None:
            self.__lastsearch.set('')
            
    def clear_data(self, po_event=None):
        """ clear all stored data """
        
        lv_table = self.__datawidget   
        
        lv_table.grid_remove()
        try:
            lv_table.delete(0, "end")   
        finally:
            lv_table.grid()        
            self.__keepsel = None
        
    def clear(self, po_event=None):
        """ clear all content of widget """
                
        lv_table = self.__datawidget  
        
        lv_table.grid_remove()
        try:
            lv_table = self.__datawidget 
            lt_ct = lv_table.cget('-columntitles')
            if isinstance(lt_ct, tuple) and len(lt_ct) > 0:            
                lv_table.deletecolumns(0, len(lt_ct)-1)        

            lv_table.delete(0, "end")     
            lv_table.resetsortinfo()
        finally:
            lv_table.grid()
            
        self.clear_()        
        
    def filltree(self, pl_data, root_func, child_indx, parent_indx):
        """ generate tree from some list 
            pl_data - content
            root_func - function that applyed to row of pl_data and return True if row linked with root node
            child_indx - index of column with child id
            parent_indx - index of column with parent id
        """
        
        self.winfo_toplevel().update_idletasks()
                
        ll_roots = []
        ld_leafs = {}

        # get roots
        ll_roots = [i for i, x in enumerate(pl_data) if root_func(x)]
        
        # get leafs
        for i, data_row in enumerate(pl_data):
            ld_leafs.setdefault(data_row[parent_indx], []).append(i)
            
        for dkey in ld_leafs:
            ld_leafs[dkey].sort()
            
        # insert roots
        lw_tl = self.__datawidget
        
        try:     
            lw_tl.grid_forget()
                        
            # insert root
            lw_tl.insertchildlist("root", "end", tuple(map(pl_data.__getitem__, ll_roots)))
                    
            # its children...
            self.filltree_(ll_roots, ld_leafs, pl_data, child_indx, parent_indx)
        except:
            raise
        finally:
            lw_tl.grid(row=0, column=0, sticky=N+E+W+S)
    
    def filltree_(self, pl_level, pd_leafs, pl_data, child_indx, parent_indx):
        """ insert data into tree from prepared data
            pl_level - current level of tree (list of indexes)
            pd_leafs - dict for leafs
            pl_data - content
            child_indx - index of column with child id
            parent_indx - index of column with parent id
        """
        
        lw_tl = self.__datawidget
        
        ll_subs = []       
        ll_subss = []
        
        ll_chids = lw_tl.columncget(child_indx, '-text')        
        
        row_index = 0
        for row_data in map(pl_data.__getitem__, reversed(pl_level)):
            lv_ch = row_data[child_indx]
            try:
                ll_leafs = pd_leafs[lv_ch]
            except KeyError:
                pass
            else:
                presearch = False    
                for i in range(-1,-3,-1):
                    lv_tmpindx = row_index+i
                    if lv_tmpindx >= 0:
                        if ll_chids[lv_tmpindx] == lv_ch:                        
                            row_index = lv_tmpindx
                            presearch = True
                            break
                    else:
                        break
                if not presearch:
                    try:
                        row_index = ll_chids.index(lv_ch)
                    except ValueError:
                        row_index = ll_chids.index(tu(lv_ch))
                                    
                ll_subss.append(ll_leafs)
                try:
                    ll_leafs[1]
                except IndexError:
                    lw_tl.insertchild(row_index, "end", pl_data[ll_leafs[0]])
                else:
                    lw_tl.insertchildlist(row_index, "end", tuple(map(pl_data.__getitem__, ll_leafs)))
        
        if ll_subss:
            ll_subs = list(itertools.chain(*reversed(ll_subss)))
            
            self.filltree_(ll_subs, pd_leafs, pl_data, child_indx, parent_indx)
    
def run_demos():
    """ some demos """
    
    root = Tk()
                    
    # demo: xtablelist
    try:
        lw_demotop = Toplevel(root)
        lw_demotop.title('xtablelist demo')
        lv_coluns = 3
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
                                   # additional
                                   allowkeepsel=True,
                                   allowresize=True,
                                   hscroll=True,
                                   vscroll=True
                                   )
        
        ll_data = []
        ll_data.append( ( 1, 'test1', 0) )
        ll_data.append( ( 2, 'test2', 0) )
        ll_data.append( ( 3, 'test3', 0) )
        ll_data.append( ( 4, 'test4', 0) )
        ll_data.append( ( 5, 'test1-1', 1) )
        ll_data.append( ( 6, 'test1-2', 1) )
        ll_data.append( ( 7, 'test3-1', 3) )
        ll_data.append( ( 8, 'test3-2', 3) )
        ll_data.append( ( 9, 'test3-3', 3) )
        ll_data.append( (10, 'test3-4', 3) )
        ll_data.append( (11, 'test3-2-1', 8) )
        ll_data.append( (12, 'test3-2-2', 8) )
        ll_data.append( (13, 'test3-2-3', 8) )
        
        lw_demowidget.configure(treecolumn=0)
        
        lw_demowidget.filltree(ll_data, lambda x: x[2]==0, 0, 2)
        
        lw_demowidget.grid(row=0, column=0, sticky=N+E+W+S)
        
        lw_demotop.columnconfigure(0, weight=1)
        lw_demotop.rowconfigure(0, weight=1)
       
    except:
        print('failed to create demo for "xtablelist":\n %s' % (get_estr()))
            
    # show demos
    root.mainloop()

if __name__ == '__main__':    
    run_demos()
    