#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2009 D Haynes
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

from hwit.checks.common import likeTyper

def bestWidget(checks, parent=None):
    name, typer = checks.items()[0] if checks else ("",None)
    if "booltyper" in name:
        return CheckBox(typer=typer, parent=parent)
    elif "scaletyper" in name:
        return ScaleSlider(typer=typer, parent=parent)
    return TextField(typer=typer, parent=parent)

class CheckBox(QCheckBox):

    @staticmethod
    def defaultTyper(val):
        return val.lower() in ("", "true", "false")

    def __init__(self, parent=None, typer=None, **kwargs):
        super(CheckBox, self).__init__(parent, **kwargs)
        if typer is None:
            self._typer = CheckBox.defaultTyper
        else:
            self._typer = typer

    def getData(self):
        return "True" if self.checkState() == Qt.Checked else "False"

    def setData(self, val):
        self.setTristate(False)
        if self._typer(val):
            if val.lower() in ("yes", "true"):
                self.setCheckState(Qt.Checked)
            elif val.lower() in ("no", "false"):
                self.setCheckState(Qt.Unchecked)
            else:
                self.setTristate(True)
                self.setCheckState(Qt.PartiallyChecked)

    data = property(getData, setData, doc = "HWIT interface")

class TextField(QLineEdit):

    class TextValidator(QValidator):

        def __init__(self, parent, typer, **kwargs):
            super(TextField.TextValidator, self).__init__(parent, **kwargs)
            self._parent = parent
            self._typer = typer
            self._likeTyper = likeTyper(typer)

        def validate(self, text, pos):
            if self._typer(unicode(text)):
                return (QValidator.Acceptable, pos)
            elif self._likeTyper(unicode(text)):
                return (QValidator.Intermediate, pos)
            else:
                self._parent.setText(text[:-1])
                return (QValidator.Invalid, pos)

    def __init__(self, parent=None, typer=None, **kwargs):
        super(TextField, self).__init__(parent, **kwargs)
        if typer is not None:
            self.setValidator(TextField.TextValidator(self, typer))

    data = property(QLineEdit.text, QLineEdit.setText, doc = "HWIT interface")

class ScaleSpinBox(QSpinBox):
    """ A spinbox control which accomodates HWIT scaletyper fields """

    class DefaultScale(object):
        labels = {0:"zero", 1:"one", 2:"two", 3:"three", 4:"four",
        5:"five"}
        max = max(labels.keys())
        min = min(labels.keys())

        def __call__(self, val):
            return unicode(val) in self.labels.values()

    def __init__(self, parent=None, typer=None, **kwargs):
        super(ScaleSpinBox, self).__init__(parent, **kwargs)
        if typer is None:
            self._typer = ScaleSpinBox.DefaultScale()
        else:
            self._typer = typer
        self.setRange(self._typer.min, self._typer.max)

    def textFromValue(self, val):
        return unicode(self._typer.labels.get(val, "undefined"))

    def valueFromText(self, text):
        """ May raise KeyError """
        lookup = dict([(v,k) for k,v in self._typer.labels.items()])
        return lookup[text]

    def validate(self, text, pos):
        return ( (QValidator.Acceptable, pos) if self._typer(text) else
        (QValidator.Invalid, pos) )

    @pyqtSlot(str)
    def onChanged(self, text):
        pass

class ScaleTuner(QWidget):

    def __init__(self, parent=None, typer=None):
        """
        From Mark Summerfield, 'Rapid GUI Programming with Python and Qt'
        """
        super(ScaleTuner, self).__init__(parent)

        self.dial = QDial()
        self.dial.setNotchesVisible(True)
        self.spinbox = ScaleSpinBox(typer=typer,valueChanged=self.dial.setValue)
        self.dial.setRange(self.spinbox.minimum(), self.spinbox.maximum())

        layout = QHBoxLayout()
        layout.addWidget(self.dial)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        self.connect(self.dial, SIGNAL("valueChanged(int)"),
                     self.spinbox.setValue)

    def __getattr__(self, name):
        """ Use Qt interface of spinbox """
        return getattr(self.spinbox, name)

    def getText(self):
        return self.textFromValue(self.value())

    def setText(self, txt):
        try:
            val = self.valueFromText(txt)
        except KeyError:
            return False
        else:
            return self.setValue(val)

    data = property(getText, setText, doc = "HWIT interface")

class ScaleSlider(QWidget):

    def __init__(self, parent=None, typer=None):
        super(ScaleSlider, self).__init__(parent)

        self.slider = QSlider(Qt.Horizontal)
        self.spinbox = ScaleSpinBox(typer=typer,valueChanged=self.slider.setValue)
        self.slider.setRange(self.spinbox.minimum(), self.spinbox.maximum())

        layout = QHBoxLayout()
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        self.setLayout(layout)

        self.connect(self.slider, SIGNAL("valueChanged(int)"),
                     self.spinbox.setValue)

    def __getattr__(self, name):
        """ Use Qt interface of spinbox """
        return getattr(self.spinbox, name)

    def getText(self):
        return self.textFromValue(self.value())

    def setText(self, txt):
        try:
            val = self.valueFromText(txt)
        except KeyError:
            return False
        else:
            return self.setValue(val)

    data = property(getText, setText, doc = "HWIT interface")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = ScaleSlider()
    #w = ScaleTuner()
    #w = ScaleSpinBox()
    #w = QSpinBox()
    w.show()
    app.exec_()
