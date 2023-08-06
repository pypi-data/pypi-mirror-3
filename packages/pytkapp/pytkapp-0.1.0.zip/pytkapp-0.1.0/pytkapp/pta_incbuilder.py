#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" release tools: incrementor for app build number """

# pytkapp: release tools: incrementor for app build number
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

import sys
import codecs
import re
import os

gp_build = re.compile('(?P<prefix>__appbuild__\s+=\s*)(?P<build>\d+)')

def incbuilder(pv_path):
    """ get and increment build tag """
    
    print('incbuilder started...')
    
    print('in path: %s' % pv_path)
    
    lv_path = os.path.abspath(pv_path)

    print('abs path: %s' % lv_path)
    
    ll_content = []
    with codecs.open(lv_path, 'rb', 'utf-8') as f_in:
        for source_line in f_in:
            lv_str = source_line
            
            lr_search = gp_build.search(lv_str)
            if lr_search is not None:
                ld_data = lr_search.groupdict()
                
                lv_prefix = ld_data['prefix']
                lv_build = int(ld_data['build'])+1
                
                lv_str = '%s%s\n' % (lv_prefix, lv_build)    
                
                print('build was changed to %s !' % lv_build)
            
            ll_content.append(lv_str)
        
    with codecs.open(lv_path, 'w+', 'utf-8') as f_out:
        f_out.writelines(ll_content)
        
    print('incbuilder finished...')

if __name__ == '__main__':
    lv_userpath = raw_input('process filename:')
    incbuilder(lv_userpath)
