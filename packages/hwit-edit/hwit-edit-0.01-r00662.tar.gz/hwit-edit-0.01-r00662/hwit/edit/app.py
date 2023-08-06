#!/usr/bin/env python
#    -*-    encoding: UTF-8    -*-

#   copyright 2010 D Haynes
#
#   This file is part of the HWIT distribution.
#

from __future__ import with_statement

licence = """
HWIT is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

HWIT is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with HWIT.  If not, see <a href="http://www.gnu.org/licenses/">
http://www.gnu.org/licenses/</a>.
"""

import sys
import os
import os.path
import uuid
import time
import csv
import re
import glob
import StringIO
import urlparse
import webbrowser
import textwrap
from string import Template
from optparse import Values
import pkg_resources

from HTMLParser import HTMLParseError
from hwit.core.model import Container
from hwit.core.context import StrictReadContext
from hwit.core.generator import Generator
from hwit.core.settings import tones
import hwit.edit.about

# import warnings
# pyQt4 on Python 2.7 OSX 10.5 emits lots of these
# warnings.simplefilter("error")
# warnings.simplefilter("ignore", PendingDeprecationWarning)

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import resources
import editors


def action(parent, text, slot=None, shortcut = None, icon=None,
    tip=None, checkable=False, signal="triggered()"):
    """ From Mark Summerfield's 'Rapid GUI Programming with Python and Qt' """
    rv = QAction(text, parent)
    if icon is not None: rv.setIcon(QIcon(":/" + icon))
    if shortcut is not None: rv.setShortcut(shortcut)
    if tip is not None: rv.setToolTip(tip); rv.setStatusTip(tip)
    if slot is not None: parent.connect(rv, SIGNAL(signal), slot)
    if checkable: rv.setCheckable(True)
    return rv

class Stylist(object):

    def __init__(self, parent):
        self.parent = parent

        self.fonts = {
        "heading": QFont("Helvetica", 32, QFont.Normal),
        "bookmark": QFont("Helvetica", 12, QFont.DemiBold),
        "rubric": QFont("Helvetica", 14, QFont.Normal),
        "label": QFont("Arial", 10, QFont.DemiBold)
        }

        self.palettes = {
        "priority": QPalette(),
        "neutral": QPalette(),
        "inert": QPalette()
        }

        self.palettes["priority"].setColor( QPalette.WindowText,
        QColor(*tones["scarlet_red"][2]))
        self.palettes["priority"].setColor( QPalette.Text,
        QColor(*tones["scarlet_red"][2]))
        self.palettes["priority"].setColor( QPalette.Base,
        QColor(*tones["butter"][0]))
        self.palettes["priority"].setColor( QPalette.Background,
        QColor(*tones["butter"][0]))

        self.palettes["neutral"].setColor( QPalette.WindowText,
        QColor(*tones["slate"][2]))
        self.palettes["neutral"].setColor( QPalette.Text,
        QColor(*tones["slate"][2]))
        self.palettes["neutral"].setColor( QPalette.Base,
        QColor(*tones["aluminium"][0]))
        self.palettes["neutral"].setColor( QPalette.Background,
        QColor(*tones["aluminium"][0]))

        self.palettes["inert"].setColor( QPalette.WindowText,
        QColor(*tones["slate"][2]))
        self.palettes["inert"].setColor( QPalette.Text,
        QColor(*tones["slate"][2]))
        self.palettes["inert"].setColor( QPalette.Base,
        QColor(*tones["aluminium"][1]))
        self.palettes["inert"].setColor( QPalette.Background,
        QColor(*tones["aluminium"][1]))

    def decorate(self, ordinal, group):
        hMetrics = QFontMetrics(self.fonts["label"])
        self.parent.groupList.setFont(self.fonts["bookmark"])
        self.parent.groupList.setPalette(self.palettes["inert"])

        self.parent.groupList.setMaximumWidth(
        max(self.parent.groupList.maximumWidth(),
        hMetrics.maxWidth() * len(group.heading)))

        for i in range(self.parent.stack.count()):
            layout = self.parent.stack.widget(i).widget().layout()
            layoutCount = layout.count()
            for n in range(layoutCount):
                widget = layout.itemAt(n).widget()
                if n == 0:
                    widget.setFont(self.fonts["heading"])
                elif n == 1:
                    widget.setFont(self.fonts["rubric"])
                elif n < layoutCount - 1:
                    widget.setFont(self.fonts["label"])

    def styleBroken(self, widget, state="", rule=""):
        if widget is None: return
        try:
            widget.setPalette(self.palettes["priority"])
        except AttributeError:
            widget.setBackgroundColor(
            self.palettes["priority"].color(QPalette.Background))
            widget.setTextColor(
            self.palettes["priority"].color(QPalette.Text))

    def styleMissing(self, widget, state="", rule=""):
        if widget is None: return
        try:
            widget.setPalette(self.palettes["neutral"])
            for (label, field), s in zip(widget.fields, state):
                if s == '_':
                    label.setPalette(self.palettes["priority"])
                else:
                    label.setPalette(self.palettes["priority"])
        except AttributeError:
            widget.setBackgroundColor(
            self.palettes["neutral"].color(QPalette.Background))
            widget.setTextColor(
            self.palettes["priority"].color(QPalette.Text))

    def styleFilled(self, widget, state="", rule=""):
        if widget is None: return
        try:
            widget.setPalette(self.palettes["inert"])
            for (label, field), s in zip(widget.fields, state):
                label.setPalette(self.palettes["inert"])
                field.setPalette(self.palettes["inert"])
        except AttributeError:
            widget.setBackgroundColor(
            self.palettes["inert"].color(QPalette.Background))
            widget.setTextColor(
            self.palettes["inert"].color(QPalette.Text))

    def styleEmpty(self, widget, state="", rule=""):
        if widget is None: return
        try:
            widget.setPalette(self.palettes["neutral"])
            for (label, field), s in zip(widget.fields, state):
                label.setPalette(self.palettes["neutral"])
                field.setPalette(self.palettes["neutral"])
        except AttributeError:
            widget.setBackgroundColor(
            self.palettes["neutral"].color(QPalette.Background))
            widget.setTextColor(
            self.palettes["neutral"].color(QPalette.Text))

class MainWindow(QMainWindow):

    def __init__(self, opts, args, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("Here's What I Think.")
        self.setAcceptDrops(True)

        self._opts = opts
        self._args = args
        self._doc = None
        self._docName = ""
        self._index = [0,0]
        self._sn = 0

        if not self._opts.ensure_value("nomenu", False):
            self.buildMenu()

        # children
        self.groupList = QListWidget(
        itemSelectionChanged=self.onGroupChanged)
        self.groupList.setSpacing(5)
        self.stack = QStackedWidget()
        self.sash = QSplitter(Qt.Horizontal)
        self.sash.addWidget(self.groupList)
        self.sash.addWidget(self.stack)
        self.sash.setStretchFactor(0,0)
        self.sash.setStretchFactor(1,1)
        self.setCentralWidget(self.sash)

        self.stylist  = Stylist(self)

        if len(self._args):
            self.read(self._args[0])

        self.animate()

    def splashScreen(self, doc):
        pic = ":/%s-448x240.png" % doc.meta.get("hwit_originator","").replace(' ','_')
        if QFile(pic).exists():
            picIcon = QIcon(pic)
            pixmap = picIcon.pixmap(448,240)
            splash = QSplashScreen(pixmap, Qt.WindowStaysOnTopHint)
            splash.setMask(pixmap.mask())
            splash.show()
            QApplication.processEvents()
            return splash
        else:
            return None

    def animate(self):
        try:
            if not self._doc: return

            for n,g in enumerate(self._doc.groups):
                state, rule = g.state, re.compile(g.rule)
                try:
                    editor = self.stack.widget(n).widget()
                except AttributeError:
                    # this method has fired prior to population of stack
                    return

                if '!' in state:
                    self.stylist.styleBroken(self.groupList.item(n))
                    self.stylist.styleBroken(editor, state, rule)
                elif '_' in state:
                    self.stylist.styleMissing(self.groupList.item(n))
                    self.stylist.styleMissing(editor, state, rule)
                elif rule.match(state) is None:
                    self.stylist.styleMissing(self.groupList.item(n))
                    self.stylist.styleMissing(editor, state, rule)
                elif '1' in state:
                    self.stylist.styleFilled(self.groupList.item(n))
                    self.stylist.styleFilled(editor, state, rule)
                elif '0' in state:
                    self.stylist.styleEmpty(self.groupList.item(n))
                    self.stylist.styleEmpty(editor, state, rule)

                if not editor.canEdit:
                    editor.buttons.button(
                    QDialogButtonBox.Apply).setEnabled(False)

        finally:
            QTimer.singleShot(200, self.animate)

    def buildMenu(self):

        # file menu
        fileMenu = self.menuBar().addMenu("&File")
        aFO = action(self, "&Open",
        self.onOpen,"Ctrl+O","doc_open.png",
        "Open a HWIT document for editing")
        fileMenu.addAction(aFO)

        aFS = action(self, "&Save",
        self.onSave,"Ctrl+S","doc_save.png",
        "Save the current HWIT document")
        fileMenu.addAction(aFS)

        aFQ = action(self, "&Quit",
        self.onQuit,"Ctrl+Q","doc_quit.png",
        "Exit the application")
        fileMenu.addAction(aFQ)

        #editMenu = self.menuBar().addMenu("&Edit")

        # tool menu
        toolMenu = self.menuBar().addMenu("&Tools")
        aTT = action(self, "Import &Template",
        self.onImport,"Ctrl+T","doc_new.png",
        "Create a new form from a template")
        toolMenu.addAction(aTT)

        aTI = action(self, "Process &Inbox",
        self.onIngest,"Ctrl+I","dir_open.png",
        "Ingest a folder of HWIT files")
        toolMenu.addAction(aTI)

        # help menu
        helpMenu = self.menuBar().addMenu("&Help")

        aHL = action(self, "Local &Help",
        self.onHelp,"Ctrl+H","dlg_help.png",
        "Browse the local documentation")
        helpMenu.addAction(aHL)

        aHW = action(self, "Help on the &Web",
        self.onWeb,"Ctrl+W","dlg_chat.png",
        "Find help on the Internet")
        helpMenu.addAction(aHW)

        aHA = action(self, "About HWIT",
        slot=self.onAbout,icon="dlg_info.png",
        tip="Information about this program")
        helpMenu.addAction(aHA)

    def clearUI(self):
        self.groupList.clear()
        for i in range(self.stack.count()-1,-1,-1):
            self.stack.removeWidget(self.stack.widget(i))
        # TODO: prompt user towards File | Open

    def buildUI(self):
        #   ..  todo:: apply fonts, colours from status observer
        for n,g in enumerate(self._doc.groups):
            ed = editors.bestEditor(g)
            ed.setAutoFillBackground(True)
            sA = QScrollArea()
            sA.setWidget(ed)
            sA.setWidgetResizable(True)
            self.stack.addWidget(sA)
            gItem = QListWidgetItem(g.heading, self.groupList)
            self.groupList.insertItem(n, gItem)
            self.stylist.decorate(n,g)

    def load(self, fObj):
        doc = None
        error = None
        c = Container(fObj)
        try:
            with StrictReadContext(c) as doc:
                doc.read()
        except (RuntimeWarning, SyntaxWarning), w:
            error = str(w)
        except HTMLParseError, e:
            error = "%s line %d, pos %d" % (e.msg, e.lineno, e.offset)

        return fObj.name, doc, error

    def open(self, path):
        try:
            input = open(path, 'r')
        except IOError, e:
            return ("", None, e)

        rv = self.load(input)
        input.close()
        return rv

    def read(self, path):
        self._docName, self._doc, error = self.open(path)

        if self._doc.title:
            self.setWindowTitle(self._doc.title)
        elif self._opts.ensure_value("autosave",""):
            self.setWindowTitle(self._opts.autosave)
        else:
            self.setWindowTitle("Here's What I Think.")

        if error:
            self.doOpenError(error)
        else:
            splash = self.splashScreen(self._doc)
            self.clearUI()
            self.buildUI()
            if splash is not None:
                time.sleep(1.1)
                splash.close()

    def save(self, doc, path):
        error = None
        try:
            fObj = open(path,'w')
            doc.write(fObj)
        except IOError, e:
            error = "couldn't save to %s\n" % path
        else:
            fObj.close()
        return error

    def doOpenError(self, error):
        QMessageBox.warning(self, "Error on File Open",
        ("The file you chose has a problem with it\n(%s).\n"
        "\nContact the creator to get it fixed.")
        % unicode(error))

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat("text/uri-list"):
            event.acceptProposedAction()

    def dropEvent(self, event):
        contents = event.mimeData()
        if contents.hasFormat("text/uri-list"):
            # FIXME: protected member access can throw RuntimeError
            ref = contents.retrieveData("text/uri-list", QVariant.Url)
            if ref.toUrl().isValid():
                self.read(unicode(ref.toUrl().toLocalFile()))

    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        data = QMimeData()
        xhtml = StringIO.StringIO()
        if self._doc is not None:
            self._doc.write(xhtml)
        data.setData("application/xhtml+xml",QByteArray(xhtml.getvalue()))
        drag.setMimeData(data)
        drag.start(Qt.CopyAction | Qt.MoveAction)

    def closeEvent(self, event):
        if self._opts.ensure_value("autosave",""):
            self.save(self._doc, self._opts.autosave)
         
        event.accept()

    @pyqtSlot()
    def onOpen(self):
        fPath = unicode(QFileDialog.getOpenFileName(self,
        "%s - Open File" % QApplication.applicationName(),
        ".", "HWIT files (*.hwit)"))

        if fPath:
            self.read(fPath)

    @pyqtSlot()
    def onSave(self):
        if not self._doc:
            return

        nb = self._doc.meta.get("hwit_namebase")
        fN = self._docName
        if nb is not None:
            nb = os.path.basename(nb)
            if nb != self._doc.meta.get("hwit_namebase"):
                # contains relative paths?
                self.stdout.write("warning: cannot use hwit_namebase\n")
            else:
                fN = "%s-%s.hwit" % (nb,uuid.uuid4().hex)
    
        fPath = unicode(QFileDialog.getSaveFileName(self,
        "%s - Save File" % QApplication.applicationName(),
        os.path.join(".",fN), "HWIT files (*.hwit)"))

        # TODO: report failure
        self.save(self._doc, fPath)

    @pyqtSlot()
    def onQuit(self):
        QApplication.quit()

    @pyqtSlot()
    def onImport(self):
        fPath = unicode(QFileDialog.getOpenFileName(self,
        "Import template", os.getcwd(), "HWIT templates (*.tsv)"))

        if not fPath: return

        try:
            input = open(fPath, 'r')
        except:
            # TODO: message
            return
        gen = Generator()
        imprt = StringIO.StringIO()
        rdr = csv.reader(input, delimiter = '\t')
        while True:
            try:
                gen.process(rdr.next())
            except StopIteration:
                input.close()
                break
        gen.write(imprt)
        imprt.seek(0)
        imprt.name = (
        os.path.splitext(os.path.basename(fPath))[0] + ".hwit" )
        self._docName, self._doc, error = self.load(imprt)
        imprt.close()
        self.clearUI()
        self.buildUI()

    @pyqtSlot()
    def onIngest(self):
        path = unicode(QFileDialog.getExistingDirectory(self,
        "Choose inbox", os.getcwd() ))

        fPSeq = glob.glob(os.path.join(path, "*.hwit"))

        nErrors = 0
        end = len(fPSeq)
        msg = "Reading the HWIT files in %s... Errors: %d"
        dlg = QProgressDialog("Collate inbox","Cancel",0,end)
        dlg.setWindowTitle("Collate inbox")

        outP = os.path.join(path, os.path.basename(path) + ".tsv")
        outFObj = open(outP,"wb")
        output = csv.writer(outFObj, delimiter="\t")
        output.writerow(
        ["# source","group id","group nr","field nr","name","value"])
        for cN, fP in enumerate(fPSeq):
            try:
                fObj = open(fP, 'r')
                src = os.path.basename(fP)
                c = Container(fObj)
                with StrictReadContext(c) as doc:
                    doc.read()
                for gN, g in enumerate(doc.groups):
                    for fN, f in enumerate(g.get()):
                        row=[src, g.id, gN, fN, f.name, f.get()]
                        output.writerow(row)
                fObj.close()
            except:
                nErrors += 1
            finally:
                dlg.setValue(cN+1)
                dlg.setLabelText(msg % (path, nErrors))

            if cN == end-1:
                path = outP
                msg = "Results written to file %s. Errors: %d."

        outFObj.close()

    @pyqtSlot()
    def onHelp(self):
        docDir = pkg_resources.resource_filename("hwit.edit", "doc")
        url = urlparse.urlunparse(
        ("file", docDir, "_build/html/hwit-guide.html","","",
        "using-the-program"))
        webbrowser.open_new_tab(url)

    @pyqtSlot()
    def onWeb(self):
        webbrowser.open_new_tab("http://hwit.berlios.de/help.html")

    @pyqtSlot()
    def onAbout(self):
        template = """\
        <h1>Info</h1>
        <dl>
        <dt>Name</dt><dd>${NAME}</dd>
        <dt>Version</dt><dd>${VERSION}</dd>
        <dt>Copyright</dt><dd>${COPYRIGHT}</dd>
        <dt>Project URL</dt><dd><a href="${WEBSITE}">${WEBSITE}</a></dd>
        </dl>
        <p>${DESCRIPTION}</p>
        <h2>Licence</h2>
        <p>${LICENCE}</p>
        """

        msg = Template(textwrap.dedent(template)).substitute(
        {
        "NAME": "HWIT editor",
        "VERSION": hwit.edit.about.version,
        "COPYRIGHT": "2009 D Haynes",
        "DESCRIPTION": """ The HWIT project is a Free software project,
        powered by the Python programming language.""",
        "WEBSITE": "http://hwit.org",
        "LICENCE": licence,
        })
        QMessageBox.about(self, "About", msg)

    @pyqtSlot()
    def onGroupChanged(self):
        selected = [self.groupList.row(i) for i in
        self.groupList.selectedItems()]
        if selected:
            index = selected[0]
            self.stack.setCurrentIndex(index)
            scrollArea = self.stack.widget(index)
            widget = scrollArea.widget()
            widget.load()

def run(task, inNode, outNode, q=None, loop=False):
    # TODO: remove
    if loop:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(":/app_icon.png"))
    options = Values(task)
    win = MainWindow(options, [inNode.path, q])
    win.show()
    if loop:
        app.exec_()

def run(fP, options, do_loop=False):
    if do_loop:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(":/app_icon.png"))
    opts = Values(options)
    win = MainWindow(opts, (fP,))
    win.show()
    if do_loop:
        app.exec_()

def main(opts, args):
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(":/app_icon.png"))
    win = MainWindow(opts, args)
    win.show()
    app.exec_()

