# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

from qtalchemy import *
from PyQt4 import QtCore, QtGui
import reports
import datetime

from sqlalchemy import MetaData, ForeignKey, create_engine, select, join

from PyHaccSchema import *
from PyHaccLib import *
from Transactions import *
from BalanceDock import *
            
class WindowChooser(QtCore.QObject):
    def __init__(self,mainWindow,child):
        QtCore.QObject.__init__(self)

        self.mainWindow = mainWindow
        self.child = child

    def __call__(self):
        self.mainWindow.workspace.setCurrentWidget(self.child)

class MainWindow(QtGui.QMainWindow):
    fileCommands = CommandMenu("_file_menu")
    accountsCommands = CommandMenu("_accounts_menu")
    transactionsCommands = CommandMenu("_transactions_menu")
    windowCommands = CommandMenu("_window_menu")
    helpCommands = CommandMenu("_help_menu")

    def __init__(self, parent=None, Session=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.setWindowIcon(QtGui.QIcon(":/pyhacc/money-2.ico"))
        self.setObjectName("MainWindow")
        self.workspace = QtGui.QTabWidget()
        self.setCentralWidget(self.workspace)
        self.workspace.setDocumentMode(True)

        self.createMenus()
        self.Session = Session

        self.balance_dock = BalanceDockWidget(self, self.Session)
        self.balance_dock.setObjectName("Balances")
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,self.balance_dock)
        self.balance_dock.refresh()
        
        self.Session.balance_refresh = self.balance_dock.refresh

        self.updateWindowTitle()
        self.setMinimumSize(160,160)
        self.resize(480,320)

        self.geo = WindowGeometry(self)

    def updateWindowTitle(self):
        session = self.Session()
        options = session.query(Options).one()
        self.setWindowTitle(self.tr("PyHacc - {0}").format(options.data_name))
        session.close()

    def tabsCollection(self):
        for i in range(self.workspace.count()):
            yield self.workspace.widget(i)

    def selectTab(self,identifier):
        desired = [tab for tab in self.tabsCollection() if tab.pyhacc_ui_id==identifier]
        if len(desired):
            self.workspace.setCurrentWidget(desired[0])
        return desired[0] if len(desired)>0 else None

    def addWorkspaceWindow(self,widget,name,identifier=None):
        widget.pyhacc_ui_id = identifier if identifier is not None else name
        #widget.chooser = WindowChooser(self,widget)
        self.workspace.addTab(widget, name)
        self.workspace.setCurrentWidget(widget)
        widget.setWindowTitle(name)
        widget.show()
        widget.setFocus()

    @fileCommands.command("&Options...", statusTip="Set Global Options")
    def options(self):
        session = self.Session()
        options = session.query(Options).one()
        dlg = BoundDialog(self)
        main = QtGui.QVBoxLayout(dlg)
        dlg.setDataReader(self.Session, Options, None)
        dlg.readData(options, load=False)
        m = dlg.mapClass(Options)
        m.addBoundForm(main, ["data_name"])
        m.connect_instance(options)

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox())
        buttonbox.addButton(QtGui.QDialogButtonBox.Ok)
        buttonbox.addButton(QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(dlg.accept)
        buttonbox.rejected.connect(dlg.reject)
        dlg.show()
        dlg.exec_()
        session.close()

        self.updateWindowTitle()

    @fileCommands.command("View Ta&gs", statusTip="View Tag List", key="Ctrl+G")
    def tagList(self):
        if not self.selectTab("Tag List"):
            self.addWorkspaceWindow(PBMdiTableView(self.Session, TagEntity), "Tag List")

    fileCommands.command("E&xit", key="Ctrl+Q", statusTip="Exit the application")(QtGui.QMainWindow.close)

    @accountsCommands.command("View &Journals", statusTip="View Journal List", key="Ctrl+J")
    def jrnList(self):
        if not self.selectTab("Journal List"):
            self.addWorkspaceWindow(PBMdiTableView(self.Session, JournalEntity), "Journal List")

    @accountsCommands.command("View &Accounts", statusTip="View Account List", key="Ctrl+A")
    def acctList(self):
        if not self.selectTab("Account List"):
            self.addWorkspaceWindow(PBMdiTableView(self.Session, AccountEntity), "Account List")

    @accountsCommands.command("View Account &Types", statusTip="View Account type List", key="Ctrl+T")
    def acctTypeList(self):
        if not self.selectTab("Account Types"):
            self.addWorkspaceWindow(PBMdiTableView(self.Session, AccountTypeEntity), "Account Types")

    @transactionsCommands.command("&Recent Transactions...", statusTip="View Recent Transactions", key="Ctrl+R")
    def tranRecent(self):
        if not self.selectTab("Recent Transactions"):
            self.addWorkspaceWindow(TransactionsByDate(self.Session), "Recent Transactions")

    @transactionsCommands.command("&Popular...", statusTip="Popular Transaction")
    def tranPopular(self):
        if not self.selectTab("Popular Transactions"):
            self.addWorkspaceWindow(TransactionsPopular(self.Session), "Popular Transactions")

    @transactionsCommands.command("&New...", statusTip="New Transaction", key="Ctrl+N", type="new")
    def tranNew(self):
        t = TransactionEditor(self,Session=self.Session)
        t.show()
        t.exec_()

    def updateEditMenu(self):
        self.editMenu.clear()

        activeWindow = self.workspace.currentWidget()
        if hasattr(activeWindow, "bindings"):
            activeWindow.bindings.fillMenu(self.editMenu)

    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowCommands.fillMenu(self.windowMenu)
        
        if self.workspace.count() > 0:
            self.windowMenu.addSeparator()

        for i in range(self.workspace.count()):
            child = self.workspace.widget(i)
            if i < 9:
                text = self.tr("&{0} {1}".format(i+1, child.windowTitle()))
            else:
                text = self.tr("&{1}".format(child.windowTitle()))

            action = self.windowMenu.addAction(text)
            action.setCheckable(True)
            action.setChecked(child == self.workspace.currentWidget())
            action.triggered.connect(WindowChooser(self,child))

    def reports(self):
        try:
            return self.report_list
        except AttributeError, e:
            self.report_list = []
            for r in reports.report_classes:
                act=QtGui.QAction(self.tr(r.name.replace("&","&&")), self)
                act.setStatusTip(self.tr(r.name+" Report"))
                act.triggered.connect(reports.ReportChooser(self,r))
                self.report_list.append(act)

            return self.report_list

    @windowCommands.command("Cl&ose", statusTip="Close the active window", key="Ctrl+W")
    def closeActiveWindow(self):
        if self.workspace.currentIndex() >= 0:
            self.workspace.removeTab(self.workspace.currentIndex())

    @windowCommands.command("Close &All", statusTip="Close all the windows")
    def closeAllWindows(self):
        while self.workspace.count() > 0:
            self.workspace.removeTab(0)

    @helpCommands.command("&About", statusTip="Show the application's About box")
    def about(self):
        QtGui.QMessageBox.about(self, self.tr("About Menu"),
                self.tr("""This is PyHacc!<br />
Version {ver}<br />
<a href="http://bitbucket.org/jbmohler/pyhacc">Bit Bucket Page</a>

<p>Running on {qtbindings}.</p>

<p>Copyright 2010-2011 Joel B. Mohler</p>""".format(ver=pyhacc_version, qtbindings=QtCore.__name__.split('.')[0])))

    @helpCommands.command("About &Qt", statusTip="Show the Qt library's About box")
    def aboutQt(self):
        QtGui.qApp.aboutQt()

    def createMenus(self):
        self.fileCommands.fillMenu(self.menuBar().addMenu(self.tr("&File")))

        self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.editMenu.aboutToShow.connect(self.updateEditMenu)

        self.accountsCommands.fillMenu(self.menuBar().addMenu(self.tr("&Accounts")))

        self.transactionsCommands.fillMenu(self.menuBar().addMenu(self.tr("&Transactions")))

        self.reportMenu = self.menuBar().addMenu(self.tr("&Reports"))
        for r in self.reports():
            self.reportMenu.addAction(r)

        self.windowMenu = self.menuBar().addMenu(self.tr("&Window"))
        self.windowMenu.aboutToShow.connect(self.updateWindowMenu)
        self.windowCommands.fillMenu(self.windowMenu)

        self.helpCommands.fillMenu(self.menuBar().addMenu(self.tr("&Help")))
