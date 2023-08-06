#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" information file for sdidemo sample """

# pytkapp: information file for sdidemo sample
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

__appname__        = 'PyTkApp Demo (SDI)'
__appversion__     = '1.0.0'
__appstate__       = ''
__appurl__         = 'http://pypi.python.org/pypi/pytkapp'
__appbuild__       = 38
__appauthor__      = 'Paul "Mid.Tier"'
__appauthoremail__ = 'mid.tier@gmail.com'
__appdesc__        = 'PyTkApp Demo (SDI)'

def get_appname():
    return globals().get('__appname__', '???')

def get_appversion():
    return globals().get('__appversion__', '???')

def get_appstate():
    return globals().get('__appstate__', '???')

def get_appurl():
    return globals().get('__appurl__', '???')

def get_appbuild():
    return globals().get('__appbuild__', '???')
    
def get_appauthor():
    return globals().get('__appauthor__', '???')

def get_appauthoremail():
    return globals().get('__appauthoremail__', '???')

def get_appdesc():
    return globals().get('__appdesc__', '???')

def get_deftitle():
    lv_appstate = get_appstate()
    if lv_appstate is not None and lv_appstate.strip() != '':        
        lv_title = '%s v.%s (build: %s) [%s]' % (get_appname(), 
                                                 get_appversion(), 
                                                 get_appbuild(), 
                                                 lv_appstate)
    else:
        lv_title = '%s v.%s (build: %s)' % (get_appname(), 
                                            get_appversion(), 
                                            get_appbuild())    
    return lv_title
