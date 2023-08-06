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
import unittest

from PyQt4.QtGui import QApplication
from hwit.edit.widgets import TextField, ScaleSpinBox, ScaleTuner, ScaleSlider
from hwit.edit.widgets import CheckBox

from hwit.checks.common import datetimetyper, scaletyper
from hwit.core.test import HWITSourceLoader

class NeedsQApplication(unittest.TestCase):

    def setUp(self):
        self.app = QApplication(sys.argv)

    def tearDown(self):
        # Causes segmentation faults in Ubuntu 12.04 LTS
        #self.app = None
        #del self.app
        pass

class TestTextField(NeedsQApplication):

    def test_001(self):
        w = TextField(None, None)
        self.assertEqual(w.data, "")
        w.data = "test data field"
        self.assertEqual(w.data, "test data field")

    def test_002(self):
        typer = datetimetyper()
        w = TextField(None, typer.isISODateTime)
        w.data = "2009-10-29 20:24:47"; self.assertEqual(w.data,"2009-10-29 20:24:47")
        w.data = "2009-10-2"; self.assertEqual(w.data,"2009-10-2")
        w.data = "2009-10-"; self.assertEqual(w.data,"2009-10-")
        w.data = "2"; self.assertEqual(w.data,"2")
        w.data = ""; self.assertEqual(w.data,"")

        w.data = "this is real data"; self.assertNotEqual(w.data,"this is real data")
        w.data = "NaN"; self.assertNotEqual(w.data,"NaN")

class TestCheckBox(NeedsQApplication):

    def test_001(self):
        c = CheckBox(None, None)
        self.assertEqual(type(c.data), type("i am a string"))

        c.data = "True"; self.assertEqual(c.data, "True")
        c.data = "2009-10-29 20:24:47"; self.assertEqual(c.data,"True")
        c.data = ""; self.assertEqual(c.data,"False")

        c.data = "False"; self.assertEqual(c.data, "False")
        c.data = "2009-10-29 20:24:47"; self.assertEqual(c.data,"False")
        c.data = ""; self.assertEqual(c.data,"False")

class TestRadioButton(NeedsQApplication):
    pass

class TestScaleSpinBox(NeedsQApplication):

    def test_001(self):
        w = ScaleSpinBox(None, None)
        self.assertEqual(w.value(), 0)
        w.setValue(5)
        self.assertEqual(w.value(), 5)

    def test_002(self):
        typer = scaletyper()
        w = ScaleSpinBox(None, typer=typer.isSevenValuedVote)
        self.assertEqual(w.value(), 0)
        w.setValue(5); self.assertNotEqual(w.value(), 5)
        w.setValue(-5); self.assertNotEqual(w.value(), -5)

class TestScaleTuner(NeedsQApplication):

    def test_001(self):
        typer = scaletyper()
        ctrl = ScaleTuner(None, typer=typer.isSevenValuedVote)
        ctrl.setValue(-4); self.assertNotEqual(ctrl.value(),-4) 
        ctrl.setValue(-3); self.assertEqual(ctrl.value(),-3)
        ctrl.setValue(-2); self.assertEqual(ctrl.value(),-2)
        ctrl.setValue(-1); self.assertEqual(ctrl.value(),-1)
        ctrl.setValue(0); self.assertEqual(ctrl.value(),0)
        ctrl.setValue(1); self.assertEqual(ctrl.value(),1)
        ctrl.setValue(2); self.assertEqual(ctrl.value(),2)
        ctrl.setValue(3); self.assertEqual(ctrl.value(),3)
        ctrl.setValue(4); self.assertNotEqual(ctrl.value(),4) # invalid

    def test_002(self):
        typer = scaletyper()
        ctrl = ScaleTuner(None, typer=typer.isSevenValuedVote)
        ctrl.data = "invalid string"; self.assertNotEqual(ctrl.data,"invalid string")
        ctrl.data = "strongly disagree"; self.assertEqual(ctrl.data,"strongly disagree")
        ctrl.data = "disagree"; self.assertEqual(ctrl.data,"disagree")
        ctrl.data = "partially disagree"; self.assertEqual(ctrl.data,"partially disagree")
        ctrl.data = "undecided"; self.assertEqual(ctrl.data,"undecided")
        ctrl.data = "partially agree"; self.assertEqual(ctrl.data,"partially agree")
        ctrl.data = "agree"; self.assertEqual(ctrl.data,"agree")
        ctrl.data = "strongly agree"; self.assertEqual(ctrl.data,"strongly agree")

class TestScaleSlider(NeedsQApplication):

    def test_001(self):
        typer = scaletyper()
        ctrl = ScaleSlider(None, typer=typer.isSevenValuedVote)
        ctrl.setValue(-4); self.assertNotEqual(ctrl.value(),-4) 
        ctrl.setValue(-3); self.assertEqual(ctrl.value(),-3)
        ctrl.setValue(-2); self.assertEqual(ctrl.value(),-2)
        ctrl.setValue(-1); self.assertEqual(ctrl.value(),-1)
        ctrl.setValue(0); self.assertEqual(ctrl.value(),0)
        ctrl.setValue(1); self.assertEqual(ctrl.value(),1)
        ctrl.setValue(2); self.assertEqual(ctrl.value(),2)
        ctrl.setValue(3); self.assertEqual(ctrl.value(),3)
        ctrl.setValue(4); self.assertNotEqual(ctrl.value(),4) # invalid

    def test_002(self):
        typer = scaletyper()
        ctrl = ScaleSlider(None, typer=typer.isSevenValuedVote)
        ctrl.data = "invalid string"; self.assertNotEqual(ctrl.data,"invalid string")
        ctrl.data = "strongly disagree"; self.assertEqual(ctrl.data,"strongly disagree")
        ctrl.data = "disagree"; self.assertEqual(ctrl.data,"disagree")
        ctrl.data = "partially disagree"; self.assertEqual(ctrl.data,"partially disagree")
        ctrl.data = "undecided"; self.assertEqual(ctrl.data,"undecided")
        ctrl.data = "partially agree"; self.assertEqual(ctrl.data,"partially agree")
        ctrl.data = "agree"; self.assertEqual(ctrl.data,"agree")
        ctrl.data = "strongly agree"; self.assertEqual(ctrl.data,"strongly agree")

def load_tests(ldr=unittest.TestLoader(), suite=None, pttrn=None):
    testCases = (TestTextField, TestCheckBox, TestRadioButton,
        TestScaleSpinBox, TestScaleTuner, TestScaleSlider)
    rv = unittest.TestSuite()
    for i in testCases:
        tests = ldr.loadTestsFromTestCase(i)
        rv.addTests(tests)
    return rv

def run():
    unittest.TextTestRunner(verbosity=2).run(load_tests())

if __name__ == "__main__":
    run()
