# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PyQt4 import QtCore, QtGui
from PyHaccSchema import *

import threading

class QueryCheck(threading.Thread):
    def __init__(self, Session, query):
        threading.Thread.__init__(self)
        self.Session = Session
        self.query = query._clone()

    def run(self):
        s = self.Session()
        self.query.session = s
        self.result = self.query.all()
        self.query.session.close()

class DockCommands(object):
    def __init__(self, Session, parent):
        self.Session = Session
        self.parent = parent

    commands = CommandMenu("_commands")
    
    @commands.itemAction("&Refresh", iconFile=":/pyhacc/refresh.ico", requireSelection=False, viewRelated=False)
    def refresh(self, id=None):
        # do nothing, just be a place-holder for save/load bracketing
        pass

class BalanceDockWidget(QtGui.QDockWidget):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> a = BalanceDockWidget(None, Session)
    """
    def __init__(self, parent, Session):
        QtGui.QDockWidget.__init__(self, parent)

        self.setWindowTitle( "Balances" )
        self.setObjectName("BalanceDock")

        self.Session = Session
        self.widget = QtGui.QWidget()
        self.setWidget(self.widget)

        vbox = QtGui.QVBoxLayout(self.widget)
        self.toolbar = LayoutWidget(vbox, QtGui.QToolBar())
        self.table = LayoutWidget(vbox, TableView(self))

        self.pre_q = Query((Accounts.id, Accounts.name, AccountTypes.name.label("type"), func.sum(Splits.sum).label("Balance"))) \
                        .join(Splits) \
                        .join(AccountTypes) \
                        .filter(AccountTypes.balance_sheet==True) \
                        .filter(AccountTypes.retained_earnings==False) \
                        .order_by(AccountTypes.sort, Accounts.name) \
                        .group_by(Accounts.id, Accounts.name, AccountTypes.name, AccountTypes.sort).subquery()
        self.q = Query(self.pre_q).filter(self.pre_q.c.Balance!=decimal.Decimal())
        self.table.setModel(QueryTableModel(self.q, ssrc=self.Session, objectConverter = lambda x: x.id), extensionId=suffixExtId(self, "Table"))

        self.entity = AccountEntity(self.Session, self.parent())
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=False)
        self.bindings.fillToolbar(self.toolbar)

        self.toolbar.addSeparator()

        self.entity2 = DockCommands(self.Session, self.parent())
        self.bindings2 = self.entity2.commands.withView(self.table, bindDefault=False)
        self.bindings2.fillToolbar(self.toolbar)
        self.bindings2.refresh.connect(self.refresh)

        self.loading = None

    def refresh(self):
        if self.loading is not None:
            return

        self.loading = QueryCheck(self.Session, self.q)
        self.loading.start()

        self.timer = QtCore.QTimer(self)
        self.timer.start(250)
        self.timer.timeout.connect(self.checkLoad)

    def checkLoad(self):
        if not self.loading.isAlive():
            self.timer.stop()
            self.timer = None
            self.table.model().reset_content_from_list(self.loading.result)
            self.loading = None
