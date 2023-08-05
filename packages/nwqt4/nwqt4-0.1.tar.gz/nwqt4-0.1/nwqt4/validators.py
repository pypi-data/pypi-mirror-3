#       validators.py
#       
#       Copyright 2010 Alexey Zotov <alexey.zotov@gmail.com>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

# -*- coding: utf-8 -*-

from PyQt4 import QtGui

import logger

class ResolutionsValidator(QtGui.QValidator):
    def __init__(self, max_len, parent=None):
        QtGui.QValidator.__init__(self, parent)
        self.max_len = max_len
    
    @logger.log_exc
    def validate(self, input, pos):
        input_str = unicode(input)
        resolutions = [res.strip() for res in input_str.split(',')]
        if len(resolutions) > self.max_len:
            pos = input_str.rindex(',')
            return (QtGui.QValidator.Invalid, pos)
        
        seen = set()
        for res in resolutions:
            if res == '':
                if len(resolutions) > 1:
                    return (QtGui.QValidator.Intermediate, pos)
                else:
                    return (QtGui.QValidator.Acceptable, pos)
            if res in seen: # duplicate
                return (QtGui.QValidator.Intermediate, pos)
            dimensions = res.split('x')
            if len(dimensions) > 2:
                pos = input_str.index(res)
                return (QtGui.QValidator.Invalid, pos)
            
            for dim in dimensions:
                if dim == '':
                    return (QtGui.QValidator.Intermediate, pos)
                try:
                    int_try = int(dim)
                except:
                    # position of dim, starting at position of res
                    pos = input_str.index(dim, input_str.index(res)) 
                    return (QtGui.QValidator.Invalid, pos)
            
            if len(dimensions) < 2:
                return (QtGui.QValidator.Intermediate, pos)
            
            seen.add(res)
        
        return (QtGui.QValidator.Acceptable, pos)

class TagsValidator(QtGui.QValidator):
    def __init__(self, max_len, parent=None):
        QtGui.QValidator.__init__(self, parent)
        self.max_len = max_len
    
    @logger.log_exc
    def validate(self, input, pos):
        input_str = unicode(input)
        tags = [tag.strip() for tag in input_str.split(',')]
        if len(tags) > self.max_len:
            pos = input_str.rindex(',')
            return (QtGui.QValidator.Invalid, pos)
        
        seen = set()
        for tag in tags:
            if tag == '':
                if len(tags) > 1:
                    return (QtGui.QValidator.Intermediate, pos)
                else:
                    return (QtGui.QValidator.Acceptable, pos)
            if tag in seen: # duplicate
                return (QtGui.QValidator.Intermediate, pos)
                
            seen.add(tag)
        
        return (QtGui.QValidator.Acceptable, pos)

def validate_widget(widget):
    state = widget.validator().validate(widget.text(), widget.cursorPosition())
    if state[0] != QtGui.QValidator.Acceptable:
        if state[0] == QtGui.QValidator.Intermediate:
            pos = widget.text().length()
        elif len(state) == 2:
            pos = state[1]
        elif len(state) == 3:
            pos = state[2]
        else:
            pos = 0
        widget.setFocus()
        widget.setCursorPosition(pos)
        return False
    return True
