#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2010 D Haynes
#
#   This file is part of the HWIT distribution.
#
#   HWIT is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   HWIT is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with HWIT.  If not, see <http://www.gnu.org/licenses/>.

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import widgets

def bestEditor(group, meta={}, parent=None ):
    if group.fillany is None:
        return GenericEditor(group, meta=meta, parent=parent)
    elif int(group.fillany) == 1:
        if all(["booltyper" in c for f in group.get() for c in f.checks]):
            return RadioGroupEditor(group, meta=meta, parent=parent)
    else:
        return GenericEditor(group, meta=meta, parent=parent)

class GenericEditor(QWidget):

    def __init__(self, group, meta, parent=None ):
        super(GenericEditor, self).__init__(parent)

        self._group = group
        self._fields = []
        self._buttons = None
        self.populate()
        self.canEdit = self.load()

    @property
    def fields(self):
        return self._fields

    @property
    def buttons(self):
        return self._buttons

    def populate(self):
        layout = QGridLayout()
        heading = QLabel(self._group.heading)
        note = QLabel(self._group.note)
        note.setWordWrap(True)
        note.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self._buttons = QDialogButtonBox(QDialogButtonBox.Apply,
        clicked=self.onAccept)

        layout.addWidget(heading,0,0,1,-1)
        layout.addWidget(note,1,1,1,4)
        noDetails = "Details not available"
        for n,field in enumerate(self._group.get()):
            f = widgets.bestWidget(field.checks)
            f.setToolTip( '\n'.join(
            [(getattr(c,"__doc__", noDetails) or noDetails).strip()
            for c in field.checks.values()]))
            
            label = QLabel(field.name)
            label.setWordWrap(True)
            layout.addWidget(label,n+3,2)
            layout.addWidget(f,n+3,4)
            
            self._fields.append((label, f))
        layout.addWidget(self._buttons,n+4,4)

        self.setLayout(layout)

    def load(self):
        rv = True
        for (l,w),f in zip(self._fields, self._group.get()):
            val = f.get()
            w.data = val
            rv = rv and f.set(val)
        return rv

    @pyqtSlot()
    def onAccept(self):
        for (l,w),f in zip(self._fields, self._group.get()):
            f.set(unicode(w.data))
            w.data = f.get()

class RadioGroupEditor(GenericEditor):

    def __init__(self, group, meta, parent=None ):
        super(RadioGroupEditor, self).__init__(group, meta, parent)

    def populate(self):
        layout = QGridLayout()
        heading = QLabel(self._group.heading)
        note = QLabel(self._group.note)
        note.setWordWrap(True)
        note.setTextInteractionFlags(Qt.TextBrowserInteraction)
        buttons = QDialogButtonBox(QDialogButtonBox.Apply,
        clicked=self.onAccept)

        layout.addWidget(heading,0,0,1,-1)
        layout.addWidget(note,1,1,1,4)
        noDetails = "Details not available"
        btnGrp = QButtonGroup()
        for n,field in enumerate(self._group.get()):
            label = QLabel(field.name)
            f = QRadioButton()
            btnGrp.addButton(f)

            layout.addWidget(label,n+3,2)
            layout.addWidget(f,n+3,4)
            self._fields.append((label, f))
        layout.addWidget(buttons,n+4,4)

        self.setLayout(layout)

    def load(self):
        for (l,w),f in zip(self._fields, self._group.get()):
            if f.get().lower() in ("yes", "true"):
                w.setChecked(True)
        return True

    @pyqtSlot()
    def onAccept(self):
        for (l,w),f in zip(self._fields, self._group.get()):
            f.set(unicode(w.isChecked()))

