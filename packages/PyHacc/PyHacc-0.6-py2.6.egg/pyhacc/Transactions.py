# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy import *
from PyQt4 import QtCore, QtGui
from qtalchemy.dialogs import *
from qtalchemy.widgets import *

import sqlalchemy.sql.expression as expr
from PyHaccSchema import *
from PyHaccUI import *

class TransactionEditor(BoundDialog):
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setWindowTitle("Transaction")
        self.setObjectName("Transaction Editor")

        self.setDataReader(Session, Transactions, "tid")

        main = QtGui.QVBoxLayout(self)
        top_grid = LayoutLayout(main,QtGui.QGridLayout())

        self.mapping = self.mapClass(Transactions)
        self.mapping.addBoundFieldGrid(top_grid,"date",0,0)
        self.mapping.addBoundFieldGrid(top_grid,"reference",0,2)
        self.mapping.addBoundFieldGrid(top_grid,"payee",1,0,columnSpan=3)
        self.mapping.addBoundFieldGrid(top_grid,"memo",2,0,columnSpan=3)

        self.tab = LayoutWidget(main, QtGui.QTabWidget())
        self.splits_table = TableView(self)
        self.tab.addTab(self.splits_table, "&Transactions")
        self.receipt = QtGui.QTextEdit(self)
        self.tab.addTab(self.receipt, "&Receipt")
        self.mapping.bind(self.receipt, "receipt")

        self.splits_model = ClassTableModel(Splits, ("account", "debit", "credit"), readonly=False)
        self.splits_table.setModel(self.splits_model, extensionId=suffixExtId(self, "Splits"))
        self.splits_table.setItemDelegate(AlchemyModelDelegate())

        self.buttonBox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.addButton(QtGui.QDialogButtonBox.Apply).clicked.connect(self.commitAndRefresh)
        self.buttonBox.addButton("To Cli&pboard", QtGui.QDialogButtonBox.ActionRole).clicked.connect(self.copyClipboard)
        
        self.actionBalance = QtGui.QAction("&Balance on Current Line", self)
        self.actionBalance.setShortcut(QtCore.Qt.CTRL + QtCore.Qt.Key_B)
        self.actionBalance.triggered.connect(self.balance)
        self.addAction(self.actionBalance)

        self.geo = WindowGeometry(self, position=False, tabs=[self.tab])

        self.readData(row, row_id)

    def load(self):
        self.mapping.connect_instance(self.main_row)
        self.splits_model.reset_content_from_list(self.main_row.splits, self.main_row.session())

    def balance(self):
        index = self.splits_table.currentIndex()
        r = index.internalPointer()
        b = decimal.Decimal('0')
        for row in self.main_row.splits:
            if row is not r:
                b += AttrNumeric(2)(row.sum)
        debitIndex = self.splits_model.index(index.row(), 1, None)
        creditIndex = self.splits_model.index(index.row(), 2, None)
        for i in [debitIndex, creditIndex]:
            w = self.splits_table.indexWidget(i)
            self.splits_table.closeEditor(w, QtGui.QAbstractItemDelegate.NoHint)
        #self.splits_table.closePersistentEditor(debitIndex)
        #self.splits_table.closePersistentEditor(creditIndex)
        if b > 0:
            self.splits_model.setData(debitIndex, 0)
            self.splits_model.setData(creditIndex, b)
        else:
            self.splits_model.setData(debitIndex, -b)
            self.splits_model.setData(creditIndex, 0)

    def copyClipboard(self):
        lines = []
        if self.main_row.date is not None:
            lines.append("Date:  {0}".format(self.main_row.date))
        if self.main_row.reference not in [None, ""]:
            lines.append("Reference:  {0}".format(self.main_row.reference))
        if self.main_row.payee not in [None, ""]:
            lines.append("Payee:  {0}".format(self.main_row.payee))
        if self.main_row.memo not in [None, ""]:
            lines.append("Memo:  {0}".format(self.main_row.memo))
        lines.append("-"*(20+1+12+1+12))
        for x in self.main_row.splits:
            lines.append("{0.account:<20} {0.debit:12.2f} {0.credit:12.2f}".format(x))
        lines.append("-"*(20+1+12+1+12))
        
        clip = QtGui.QApplication.clipboard()
        #print '\n'.join(lines)
        clip.setText('\n'.join(lines))

from qtalchemy.PBSearchDialog import PBSearchableListDialog

class TransactionsByDate(PBMdiTableView):
    def __init__(self,Session):
        extensionId = "{0}/MDIRecent".format(self.__class__.__name__)

        PBSearchableListDialog.__init__(self, extensionId=extensionId)

        self.Session = Session
        self.entity = TransactionEntity(Session, self)
        self.base_query, converter = self.entity.list_query_converter()
        self.base_query = self.base_query.order_by(expr.desc(Transactions.date))
        self.table.setModel(QueryTableModel(self.base_query, ssrc=Session,objectConverter=converter), extensionId=suffixExtId(self,"Table"))
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)

        self.table.model().reset_content_from_session()

from sqlalchemy.orm import column_property

class TransactionsPopular(PBMdiTableView):
    def __init__(self,Session):
        extensionId = "{0}/MDIPopular".format(self.__class__.__name__)

        PBSearchableListDialog.__init__(self, extensionId=extensionId)

        self.Session = Session
        self.entity = TransactionEntity(Session, self)
        q = Query((Transactions.payee,Transactions.memo,func.count().label("count"))).filter(Transactions.date>datetime.date.today()-datetime.timedelta(366)).group_by(Transactions.payee,Transactions.memo).order_by(expr.desc("count")).subquery()
        q2= Query((q.c.count.label("count"),q.c.payee,q.c.memo)).order_by(expr.desc(q.c.count)).subquery()
        
        class Thing(object):
            __tablename__ = "sam"

            @property
            def tid(self):
                s = Session()
                r = s.query(Transactions.tid).filter(Transactions.memo==self.memo).filter(Transactions.payee==self.payee).order_by(expr.desc(Transactions.date)).limit(1).one()[0]
                s.close()
                return r

        mapper(Thing, q2, primary_key=[q2.c.memo, q2.c.payee])

        self.base_query, converter = Query(Thing), lambda x: x.tid
        #self.base_query = self.base_query.order_by(expr.desc(Transactions.date))
        self.table.setModel(QueryTableModel(self.base_query, ssrc=Session,objectConverter=converter), extensionId=suffixExtId(self,"Table"))
        self.bindings = self.entity.itemCommands.withView(self.table, bindDefault=True)

        self.table.model().reset_content_from_session()
