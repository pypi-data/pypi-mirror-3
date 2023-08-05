# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from qtalchemy import PBTableTab
from qtalchemy.dialogs import *
from qtalchemy.widgets import *
from PyQt4 import QtCore, QtGui
from PyHaccSchema import *

class ReconcileCommands(object):
    def __init__(self, Session, parent):
        self.Session = Session
        self.parent = parent

    commands = CommandMenu("_commands")
    
    @commands.itemAction("&Refresh", iconFile=":/pyhacc/refresh.ico", requireSelection=False, viewRelated=False)
    def refresh(self, id=None):
        # do nothing, just be a place-holder for save/load bracketing
        pass

class AccountEditor(BoundDialog):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> a = AccountEditor(None,row=s.query(Accounts).filter(Accounts.name=="Cash").one())
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setObjectName("AccountsInfo")
        self.setDataReader(Session, Accounts, "id")

        main = QtGui.QVBoxLayout(self)
        top_grid = LayoutLayout(main,QtGui.QGridLayout())

        self.mm = self.mapClass(Accounts)
        self.mm.addBoundFieldGrid(top_grid,"name",0,0)
        self.mm.addBoundFieldGrid(top_grid,"type",0,2)

        self.tab = LayoutWidget(main,QtGui.QTabWidget())

        self.accounting_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.accounting_tab),["journal_name","retearn_name","description"])
        self.tab.addTab( self.accounting_tab,"&Accounting" )

        self.institution_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.institution_tab),"instname,instaddr1,instaddr2,instcity".split(','))
        self.tab.addTab( self.institution_tab,"&Institution" )

        self.rec_tab = QtGui.QWidget()
        self.mm.addBoundForm(QtGui.QVBoxLayout(self.rec_tab),"rec_note".split(','))
        self.tab.addTab( self.rec_tab,"&Reconciliation" )

        self.transactions_tab = PBTableTab(self, Session, TransactionEntity, 
                        [(Splits.account_id, lambda dataContext: dataContext.id)], 
                        Query((Transactions.tid.label("id"),Transactions.date, Transactions.reference, Transactions.payee, Transactions.memo, Splits.sum)).join(Splits).order_by(Transactions.date.desc()), 
                        extensionId=suffixExtId(self, "Transactions"))
        self.tab.addTab(self.transactions_tab,"Tran&sactions")

        buttonbox = LayoutWidget(main,QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel))
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self, position=False, tabs=[self.tab])

        self.readData(row, row_id)

    def load(self):
        self.mm.connect_instance(self.main_row)
        self.transactions_tab.refresh(self.main_row)
        self.setWindowTitle( "Account Information - {0.name}".format(self.main_row) )

class AccountReconcile(BoundDialog):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> a = AccountReconcile(None,row=s.query(Accounts).filter(Accounts.name=="Cash").one())
    """
    def __init__(self,parent,row=None,Session=None,row_id=None,flush=True):
        BoundDialog.__init__(self,parent)

        self.setObjectName("AccountReconciliation")
        self.setDataReader(Session, Accounts, "id")

        main = QtGui.QHBoxLayout(self)
        left_controls = LayoutLayout(main,QtGui.QVBoxLayout())

        self.mm = self.mapClass(SplitTagger.ReconciliationStatus)
        self.mm.addBoundForm(left_controls,["reconciled_balance","pending_balance","outstanding_balance"])
        self.mm_account = self.mapClass(Accounts)
        self.mm_account.addBoundForm(left_controls,["rec_note"])

        right_controls = LayoutLayout(main, QtGui.QVBoxLayout())
        self.toolbar = LayoutWidget(right_controls, QtGui.QToolBar())
        self.checkTable = LayoutWidget(right_controls, TableView(extensionId=suffixExtId(self, "Table")))
        self.model = ClassTableModel(SplitTagger,"pending,reconciled,debit,credit,date,reference,payee,memo".split(','), readonly=False, fixed_rows=True)
        self.checkTable.setModel(self.model)
        main.setStretch(1,15) # massively favor the table side of things

        self.buttonBox = LayoutWidget(left_controls,QtGui.QDialogButtonBox())

        self.okBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.accept)
        self.reconcileBtn = self.buttonBox.addButton("&Reconcile",QtGui.QDialogButtonBox.ActionRole)
        self.reconcileBtn.clicked.connect(self.reconcile_now)
        self.cancelBtn = self.buttonBox.addButton(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.rejected.connect(self.reject)

        self.geo = WindowGeometry(self)

        self.entity = TransactionEntity(Session, self)
        self.binding = self.entity.itemCommands.withView(self.checkTable, objectConverter=lambda x:x.split.Transaction.tid)
        self.binding.fillToolbar(self.toolbar)
        self.binding.preCommand.connect(self.preCommandSave)
        self.binding.refresh.connect(self.refresh)

        self.toolbar.addSeparator()

        self.entity2 = ReconcileCommands(self.Session, self.parent())
        self.bindings2 = self.entity2.commands.withView(self.checkTable, bindDefault=False)
        self.bindings2.fillToolbar(self.toolbar)
        self.bindings2.preCommand.connect(self.preCommandSave)
        self.bindings2.refresh.connect(self.refresh)

        self.readData(row, row_id)

    def load(self):
        self.recStatus = SplitTagger.ReconciliationStatus()

        self.tagRec = self.session.query(Tags).filter(Tags.name==Tags.Names.BankReconciled).one()
        self.tagPen = self.session.query(Tags).filter(Tags.name==Tags.Names.BankPending).one()
        q = self.session.query(Tagsplits, Tags.name.label('tag_name_s')).join(Tags).filter(Tags.name==Tags.Names.BankReconciled).subquery()
        self.outstanding_split_list = self.session.query(Splits) \
                            .outerjoin(q) \
                            .join(Accounts) \
                            .join(Transactions) \
                            .filter(Accounts.id==self.main_row.id) \
                            .filter(q.c.tag_name_s==None) \
                            .order_by(Transactions.date) \
                            .all()

        progress = QtGui.QProgressDialog("Loading...", "", 0, len(self.outstanding_split_list), self)
        progress.setCancelButton(None)
        progress.setMinimumDuration(1)
        progress.setWindowModality(QtCore.Qt.WindowModal)

        self.shown_check_split_list = []
        for i in range(len(self.outstanding_split_list)):
            progress.setValue(i)
            split = self.outstanding_split_list[i]
            self.shown_check_split_list.append(SplitTagger(split,self.tagRec,self.tagPen,self.recStatus))

        self.reconciled_split_list = self.session.query(Splits) \
                            .outerjoin(q) \
                            .join(Accounts) \
                            .filter(Accounts.id==self.main_row.id) \
                            .filter(q.c.tag_name_s==Tags.Names.BankReconciled) \
                            .all()
        self.recStatus.reconciled_balance = sum([split.sum for split in self.reconciled_split_list],decimal.Decimal())
        self.recStatus.pending_balance = self.recStatus.reconciled_balance + sum([split.amount for split in self.shown_check_split_list if split.pending],decimal.Decimal())
        self.recStatus.outstanding_balance = self.recStatus.reconciled_balance + sum([split.amount for split in self.shown_check_split_list],decimal.Decimal())

        self.model.reset_content_from_list(self.shown_check_split_list)
        for x in self.shown_check_split_list:
            instanceEvent(x, "set", "pending")(lambda obj, attr, value: self.model.rowEmitChange(obj, "all"))
            instanceEvent(x, "set", "reconciled")(lambda obj, attr, value: self.model.rowEmitChange(obj, "all"))

        progress.setValue(len(self.outstanding_split_list))

        self.mm.connect_instance(self.recStatus)
        self.mm_account.connect_instance(self.main_row)

        self.setWindowTitle( "Account Reconciliation - {0}".format(self.main_row.name) )

    def reconcile_now(self):
        for s in self.shown_check_split_list:
            if s.pending:
                s.reconciled = True
                s.pending = False
