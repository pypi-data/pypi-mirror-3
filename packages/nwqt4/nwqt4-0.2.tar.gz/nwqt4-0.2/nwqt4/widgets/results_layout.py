#       results_layout.py
#       
#       Copyright 2011 Alexey Zotov <alexey.zotov@gmail.com>
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

LEN_2_LAYOUT = {
    1: [1],
    2: [2],
    3: [3],
    4: [2, 2],
    5: [2, 1, 2],
    6: [3, 3],
    7: [2, 3, 2],
    8: [3, 2, 3],
    9: [3, 3, 3]
}

class ResultsLayout(QtGui.QVBoxLayout):
    def __init__(self, capacity, parent=None):
        super(ResultsLayout, self).__init__(parent)
        if capacity < 1:
            capacity = 1
        if capacity > 9:
            capacity = 9
        self.capacity = capacity
        self.count = 0
        self.hlayouts = []
        for ind in LEN_2_LAYOUT[capacity]:
            hlayout = QtGui.QHBoxLayout(parent)
            hlayout.setContentsMargins(5, 5, 5, 5)
            hlayout.setSpacing(10)
            hlayout.addStretch()
            self.hlayouts.append(hlayout)
            self.addLayout(hlayout)

    def addWidget(self, item):
        if self.count >= self.capacity:
            return
        count = self.count
        for ind, hlayout in enumerate(self.hlayouts):
            hcapacity = LEN_2_LAYOUT[self.capacity][ind]
            if count < hcapacity:
                hlayout.addWidget(item)
                hlayout.addStretch()
                self.count += 1
                break
            else:
                count -= hcapacity
