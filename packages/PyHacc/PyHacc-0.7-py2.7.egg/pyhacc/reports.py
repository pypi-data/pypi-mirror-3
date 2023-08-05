# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################

import sys
from qtalchemy import *
from qtalchemy.xplatform import *
from qtalchemy.widgets import *
from qtalchemy.ext.reporttools import *
from PyQt4 import QtCore, QtGui
import datetime
import csv
from sqlalchemy.sql import select
from sqlalchemy.orm.exc import UnmappedInstanceError

from PyHaccSchema import *
from PyHaccLib import *
from fuzzyparsers import *
import cgi

class ReportChooser(QtCore.QObject):
    """
    This class provides a callable hook for an action to initialize a report.
    """

    def __init__(self,mainWindow,prompt_callable):
        QtCore.QObject.__init__(self)

        self.mainWindow = mainWindow
        self.prompt_callable = prompt_callable

    def __call__(self):
        report = self.prompt_callable(self.mainWindow.Session)
        report.construct()
        self.mainWindow.addWorkspaceWindow(report.unified_tab(self.mainWindow),self.prompt_callable.name)

class Attr:
    def __init__(self, **kwargs):
        for k,v in kwargs.iteritems():
            setattr(self,k,v)

def GeraldoTemplate(rpt, pagesize):
    from geraldo import Report, DetailBand, ObjectValue,FIELD_ACTION_COUNT, FIELD_ACTION_SUM,  ReportGroup,  ReportBand, SystemField, BAND_WIDTH, Label
    from geraldo.utils import cm, inch
    from geraldo.generators import PDFGenerator
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

    if pagesize is None:
        pagesize = rpt.page_size

    if not isinstance(pagesize, tuple):
        pagesize = ReportLabSize(pagesize)

    class Template(Report):
        title = cgi.escape(rpt.report_title)
        page_size = pagesize
        margin_top = .75*inch
        margin_bottom = .75*inch
        margin_left = .75*inch
        margin_right = .75*inch

        class band_page_header(ReportBand):
            height = 1.3*cm
            elements = [
                SystemField(expression='%(report_title)s', top=0.1*cm, left=0, width=BAND_WIDTH,
                    style={'fontName': 'Helvetica-Bold', 'fontSize': 14, 'alignment': TA_CENTER}), 
            ]
            borders = {'bottom': True}

        class band_page_footer(ReportBand):
            height = 0.5*cm
            elements = [
                    #Label(text='Geraldo Reports', top=0.1*cm),
                    SystemField(expression=u'Printed %(now:%Y, %b %d)s at %(now:%H:%M)s', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_LEFT}),
                    SystemField(expression=u'Page %(page_number)d of %(page_count)d', top=0.1*cm,
                        width=BAND_WIDTH, style={'alignment': TA_RIGHT}),
                    ]
            borders = {'top': True}

    return Template

class PyHaccReport(ModelObject):
    prompt_order = ()
    entity_class = None
    refresh_model_dimensions = False

    def __init__(self, Session=None):
        if Session is not None:
            # hook myself up to a session
            Session().npadd(self)

    def construct(self, **kwargs):
        pass

    @property
    def filename(self):
        if hasattr(self, "name"):
            return re.sub("[^A-Za-z0-9]", "_", self.name)
        else:
            return re.sub("[^A-Za-z0-9]", "_", self.__class__.__name__)

    @property
    def report_title(self):
        return self.name

    @property
    def page_size(self):
        return "letter"

    def objectConverter(self):
        return None

    def user_prompts(self, map, layout):
        m = map.mapClass(type(self))
        for col in self.prompt_order:
            m.addBoundField(layout,col)
        m.connect_instance(self)

    def tableExtensionId(self):
        """
        It is highly recommended that you override this and return a column 
        appropriate name if and only if self.refresh_model_dimensions is True.
        """
        return "DataTable"

    def unified_tab(self, parent):
        """
        Initialize a QWidget for inclusion in a tabbed MDI setting.
        """
        class PromptWidget(QtGui.QWidget,MapperMixin):
            def __init__(self, parent, report):
                QtGui.QWidget.__init__(self, parent)
                self.setProperty("ExtensionId", "Report_"+type(report).__name__)

                self.report = report

                main = QtGui.QHBoxLayout(self)
                self.splitter=LayoutWidget(main,QtGui.QSplitter())
                
                self.prompt_side = QtGui.QWidget()
                
                # left hand side: prompt area
                self.prompt_area = QtGui.QVBoxLayout(self.prompt_side)
                # self.prompt_area.setMargin(15)
                self.report.user_prompts(self, LayoutLayout(self.prompt_area,QtGui.QFormLayout()))

                buttons = LayoutLayout(self.prompt_area,QtGui.QHBoxLayout())
                refresh = LayoutWidget(buttons,QtGui.QPushButton("&Refresh",self))
                refresh.clicked.connect(self.refreshModel)
                pdf = LayoutWidget(buttons,QtGui.QPushButton("&PDF",self))
                pdf.clicked.connect(self.pdf_button)

                # right hand side: output
                self.table = TableView()

                self.splitter.addWidget(self.prompt_side)
                self.splitter.addWidget(self.table)

                self.geo = WindowGeometry(self,splitters=[self.splitter],size=False)
                
                self.refreshModel()

            def refreshModel(self):
                self.submit()
                if self.table.model() is None or self.report.refresh_model_dimensions:
                    self.table.setModel(PBTableModel(self.report.columns(),objectConverter=self.report.objectConverter()), 
                                        extensionId=suffixExtId(self, self.report.tableExtensionId()))

                    # Note that bindings have a dependency on the table model
                    if self.report.entity_class is not None:
                        for a in self.table.actions():
                            self.table.removeAction(a)
                        self.entity = self.report.entity_class(self.report.session().__class__, parent)
                        self.bindings = self.entity.itemCommands.withView(self.table)
                        self.bindings.refresh.connect(self.refreshModel)
                self.table.model().reset_content_from_list(self.report.data())

            def pdf_button(self):
                import tempfile
                import os
                tempdir = tempfile.mkdtemp()
                fullpath = os.path.join(tempdir, self.report.filename + ".pdf")
                self.report.geraldo(fullpath, None, detailRatios = [self.table.columnWidth(i) for i in range(self.table.model().columnCount(None))])
                xdg_open(fullpath)

        outer = PromptWidget(parent, self)
        return outer

    def csv(self,stream,dialect=None):
        lines = self.data()
        cols = self.columns()
        csv_stream = csv.writer(stream)
        csv_stream.writerow([c.label for c in cols])
        for p in lines:
            csv_stream.writerow([getattr(p,c.attr) for c in cols])

    def pdf(self,fName,pagesize):
        try:
            from reportlab.pdfgen.canvas import Canvas
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, Table, TableStyle
        except ImportError, e:
            raise Exception("You need to install reportlab.")

        styles = getSampleStyleSheet()
        styleN = styles['Normal']
        styleH = styles['Heading1']
        story = []

        lines = self.data()
        cols = self.columns()

        story.append(Paragraph(cgi.escape(self.name),styleH))

        header = [Paragraph("<b>{0}</b>".format(c.label),styleN) for c in cols]
        #widths = [1.25*inch,2.5*inch]+[.80*inch]*interval_count
        t=Table([header]+[[str(getattr(p,c.attr)) for c in cols] for p in lines],repeatRows=1)
        for i in range(len(cols)):
            if cols[i].type_ is decimal.Decimal:
                # TODO:  For some reason this alignment code appears to be a failure.
                # I suspect that proper decimal counts in the strings would go a long way.
                #print (i,i+1),(1,-1)
                t.setStyle(TableStyle([('ALIGN',(i,i+1),(1,-1),'DECIMAL')]))
        story.append(t)

        doc = SimpleDocTemplate(fName,pagesize = ReportLabSize(pagesize))
        doc.build(story)

    def geraldo(self, fName, pagesize, **kwargs):
        from geraldo import Report, DetailBand, ObjectValue, FIELD_ACTION_COUNT, FIELD_ACTION_SUM, ReportGroup, ReportBand, SystemField, BAND_WIDTH
        from geraldo.utils import inch
        from geraldo.generators import PDFGenerator
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT

        if pagesize is None:
            pagesize = self.page_size
        pagesize = ReportLabSize(pagesize)

        cols = self.columns()

        if not kwargs.has_key("detailRatios"):
            dr = [m.width for m in cols]
            if set(dr) != set([None]):
                kwargs['detailRatios'] = dr

        if kwargs.has_key("detailRatios"):
            detailRatios = kwargs["detailRatios"]
            widths = sum(detailRatios)
            for i in range(len(cols)):
                detailRatios[i] = detailRatios[i] * (pagesize[0] - 1.5*inch) / widths
        else:
            detailRatios = [(pagesize[0] - 1.5*inch) / len(cols)] * len(cols)

        det_elements = []
        for i in range(len(cols)):
            wf = u
            style = {}
            if cols[i].type_ is decimal.Decimal:
                style['alignment'] = TA_RIGHT
                wf = sz
            else:
                style['wordWrap'] = True
            
            det_elements.append(ObjectValue(
                        attribute_name=cols[i].attr, 
                        get_value=wf(cols[i].attr), 
                        top=0, 
                        left=sum([detailRatios[j] for j in range(i)]), 
                        width=detailRatios[i], 
                        style=style))

        class GeraldoBS(GeraldoTemplate(self, pagesize)):
            class band_detail(DetailBand):
                height=0.2*inch
                auto_expand_height = True
                elements = det_elements

        bs = GeraldoBS(queryset = self.data())
        bs.generate_by(PDFGenerator, filename=fName)


def dc_object(obj,attr_amount,attr_debit="debit",attr_credit="credit",exponent=-2):
    assert exponent < 0
    amt = getattr(obj,attr_amount)
    zero = decimal.Decimal("0."+'0'*(-exponent))
    if amt > 0:
        setattr(obj,attr_debit,amt)
        setattr(obj,attr_credit,zero)
    elif amt < 0:
        setattr(obj,attr_debit,zero)
        setattr(obj,attr_credit,amt*(-1))
    else:
        setattr(obj,attr_debit,zero)
        setattr(obj,attr_credit,zero)

def sessionedObjectInit(session, class_, **kwargs):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> accountRpt = sessionedObjectInit(s,AccountList,type_name="Asset")
    >>> [(x.name, x.description) for x in accountRpt.data()]
    [(u'Cash', u'Petty Cash'), (u'Checking', u'Checking Account')]
    """
    obj = class_()
    try:
        session.add(obj)
    except UnmappedInstanceError as e:
        session.npadd(obj)
    obj.construct(**kwargs)
    return obj

def primaryKeyReferral(obj, class_, **kwargs):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> class Properties(ModelObject):
    ...     type_name = AccountTypeReferral("Account Type","type_obj")
    ...
    >>> obj = Properties()
    >>> s.npadd(obj)
    >>> obj.type_obj = primaryKeyReferral(obj, AccountTypes, name="Expense")
    >>> obj.type_name
    u'Expense'
    >>> obj.type_obj = primaryKeyReferral(obj, AccountTypes, balance_sheet=False)
    Traceback (most recent call last):
    ...
    MultipleResultsFound: Multiple rows were found for one()
    >>> obj.type_obj = primaryKeyReferral(obj, AccountTypes, id=None)
    >>> obj.type_obj, obj.type_name
    (None, None)
    >>> obj.type_obj = primaryKeyReferral(obj, AccountTypes, id=0, name='Sam')
    Traceback (most recent call last):
    ...
    ValueError: multiply specified key:  {'id': 0, 'name': 'Sam'}
    """
    session = obj.session()
    q = session.query(class_)
    lookups = [(k,v) for k, v in kwargs.items() if v is not None]
    if 0 == len(lookups):
        return None
    elif 1 == len(lookups):
        k, v = lookups[0]
        q = q.filter(getattr(class_,k)==v)
        return q.one()
    raise ValueError("multiply specified key:  {0}".format(kwargs))

class AccountList(PyHaccReport):
    name="Account Listing"
    type_name = AccountTypeReferral("Account Type","type_obj")
    prompt_order = ("type_name",)
    entity_class = AccountEntity

    def construct(self, type_id=None, type_name=None):
        self.type_obj = primaryKeyReferral(self, AccountTypes, id=type_id, name=type_name)

    def data(self):
        s = self.session().__class__()
        q = s.query(Accounts.id,Accounts.name,Accounts.description,AccountTypes.name.label("type")).join(AccountTypes)
        if self.type_obj is not None:
            q = q.filter(Accounts.type_id==self.type_obj.id).order_by(Accounts.name)
        else:
            q = q.order_by(AccountTypes.name,Accounts.name)
        result = q.all()
        s.close()
        return result

    def columns(self):
        return [ModelColumn("name",str),
            ModelColumn("description",str), 
            ModelColumn("type",str)]

    def objectConverter(self):
        return lambda x: x.id

class JournalList(PyHaccReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,JournalList)
    >>> [(x.name, x.description) for x in rpt.data()]
    [(u'General', None)]
    """
    name="Journal Listing"
    entity_class = JournalEntity

    def data(self):
        s = self.session().__class__()
        q = s.query(Journals)
        result = q.all()
        s.close()
        return result

    def columns(self):
        return [ModelColumn("name",str),
            ModelColumn("description",str)]

    def objectConverter(self):
        return lambda x: x.id

class AccountTypeList(PyHaccReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,AccountTypeList)
    >>> [(x.name, x.balance_sheet) for x in rpt.data() if x.name.startswith('A')]
    [(u'Asset', True)]
    """
    name="Account Types Listing"
    entity_class = AccountTypeEntity

    def data(self):
        s = self.session().__class__()
        q = s.query(AccountTypes)
        result = q.all()
        s.close()
        return result

    def columns(self):
        return [ModelColumn("name",str),
            ModelColumn("description",str)]

    def objectConverter(self):
        return lambda x: x.id

class AccountBalanceListReport(PyHaccReport):
    entity_class = AccountEntity

    def post_process_data(self, d):
        # post-process a bit
        lines = d
        lines = [l for l in lines if l.amount != 0]
        for l in lines:
            dc_object(l, "amount")
        return lines

    def columns(self):
        return [ModelColumn("accounttypes_name",str,label="Account Type"),
            ModelColumn("accounts_name",str,label="Account"),
            ModelColumn("debit",decimal.Decimal,label="Debit"),
            ModelColumn("credit",decimal.Decimal,label="Crebit")]

    def objectConverter(self):
        return lambda x: x.accounts_id

    @property
    def report_title(self):
        return self.title_shell.format(self)

    def geraldo(self, outfile, pagesize, **kwargs):
        from geraldo import Report, DetailBand, ObjectValue,FIELD_ACTION_COUNT, FIELD_ACTION_SUM,  ReportGroup,  ReportBand, SystemField, BAND_WIDTH
        from geraldo.utils import cm
        from geraldo.generators import PDFGenerator
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT

        class GeraldoBS(GeraldoTemplate(self, pagesize)):
            class band_detail(DetailBand):
                height=0.5*cm
                elements = [
                            ObjectValue(attribute_name='accounts_name', top=0, left=1*cm),
                            ObjectValue(attribute_name='debit', get_value=lambda r: r.amount if r.amount > 0 else "0.00", display_format="%s", top=0, left=6*cm, style={'alignment': TA_RIGHT}),
                            ObjectValue(attribute_name='credit', get_value=lambda r: -r.amount if r.amount < 0 else "0.00", display_format="%s", top=0, left=10*cm, style={'alignment': TA_RIGHT})
                            ]
            groups = [
                ReportGroup(attribute_name='accounttypes_name',
                    band_header=ReportBand(
                        height=0.7*cm,
                        elements=[
                            ObjectValue(attribute_name='accounttypes_name', left=0, top=0.1*cm,
                                #get_value=lambda instance: 'Superuser: ' + (instance.is_superuser and 'Yes' or 'No'),
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 12})
                        ],
                        borders={'bottom': True},
                    ),
                    band_footer=ReportBand(
                        height=0.7*cm,
                        elements=[
                            ObjectValue(attribute_name='debit', action=FIELD_ACTION_SUM, display_format="%s", top=0, left=6*cm, style={'alignment': TA_RIGHT}),
                            ObjectValue(attribute_name='credit', action=FIELD_ACTION_SUM, display_format="%s", top=0, left=10*cm, style={'alignment': TA_RIGHT})
                        ],
                        borders={'top': True},
                    ),
                )]
        
        bs = GeraldoBS(queryset = self.data())
        bs.generate_by(PDFGenerator, filename=outfile)

class BalanceSheet(AccountBalanceListReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource()
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,BalanceSheet)
    >>> for x in rpt.data():
    ...     print "{0.accounts_name:20s} {0.amount:>10.2f}".format(x)
    Cash                     -11.24
    Checking               14200.00
    Capital               -14188.76
    """
    name = "Balance Sheet"
    title_shell = "{0.name} for {0.date:%x}"
    journal = JournalReferral("Journal","journal_obj")
    date = UserAttr(datetime.date, "Date")
    prompt_order = ("date","journal")

    def construct(self,date="dec 31",journal_id=None,journal=None):
        self.date = sanitized_date(date)
        self.journal_obj = primaryKeyReferral(self, Journals, id=journal_id, name=journal)

    def data(self):
        s = self.session().__class__()
        # set up the main query
        if self.journal_obj is None:
            tranCriteria = Transactions.date<=self.date
        else:
            tranCriteria = expr.and_(Transactions.date<=self.date,Accounts.journal_id==self.journal_obj.id)
        q=s.query(
                Splits.sum,
                expr.case(whens=[(AccountTypes.balance_sheet==False, Accounts.retearn_id)],else_=Accounts.id).label("account_id")
                ).join(Accounts).join(AccountTypes).join(Transactions).filter(tranCriteria).subquery()
        t=s.query(
                Accounts.id.label("accounts_id"),
                Accounts.name.label("accounts_name"),
                AccountTypes.id.label("accounttypes_id"),
                AccountTypes.name.label("accounttypes_name"),
                func.sum(q.c.sum).label("amount")
                ).join((q,Accounts.id==q.c.account_id)).join(AccountTypes) \
                .group_by(Accounts.id,Accounts.name,AccountTypes.id,AccountTypes.name,AccountTypes.sort) \
                .order_by(AccountTypes.sort, Accounts.name)

        d = t.all()
        s.close()
        return self.post_process_data(d)

class TransactionsByAccount(PyHaccReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource(datetime.date(2011,3,31))
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,TransactionsByAccount,account='Cash', begin_date='jan 1 2011', end_date='dec 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.date:%Y.%m.%d} {0.payee:10s} {0.memo:10s} {0.sum:>8.2f}".format(x)
    2011.03.31 Giant      Groceries    -11.24
    >>> rpt = sessionedObjectInit(s,TransactionsByAccount,account='Checking', begin_date='jan 1 2011', end_date='dec 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.date:%Y.%m.%d} {0.payee:15s} {0.memo:15s} {0.sum:>8.2f}".format(x)
    2011.01.02 ACME Inc        Payroll           400.00
    2011.01.09 ACME Inc        Payroll           400.00
    2011.01.16 ACME Inc        Payroll           400.00
    2011.01.23 ACME Inc        Payroll           400.00
    2011.01.30 Central Bank    Mortgage         -550.00
    2011.01.30 ACME Inc        Payroll           400.00
    2011.02.06 ACME Inc        Payroll           400.00
    2011.02.13 ACME Inc        Payroll           400.00
    2011.02.20 ACME Inc        Payroll           400.00
    2011.02.27 ACME Inc        Payroll           400.00
    2011.03.01 Central Bank    Mortgage         -550.00
    2011.03.06 ACME Inc        Payroll           400.00
    2011.03.13 ACME Inc        Payroll           400.00
    2011.03.20 ACME Inc        Payroll           400.00
    2011.03.27 ACME Inc        Payroll           400.00
    2011.03.31 Central Bank    Mortgage         -550.00
    2011.04.03 ACME Inc        Payroll           400.00
    >>> rpt = sessionedObjectInit(s,TransactionsByAccount,account='Checking', group_payee=True, begin_date='jan 1 2011', end_date='dec 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.payee:15s} {0.sum:>8.2f}".format(x)
    ACME Inc         5600.00
    Central Bank    -1650.00
    """
    name="Account Transactions"
    account = AccountReferral("Account","account_obj")
    begin_date = UserAttr(Nullable(datetime.date), "Begin Date")
    end_date = UserAttr(Nullable(datetime.date), "End Date")
    group_payee = UserAttr(bool, "Group by payee")
    group_memo = UserAttr(bool, "Group by memo")
    prompt_order = ("begin_date","end_date","account","group_payee","group_memo")
    entity_class = TransactionEntity
    refresh_model_dimensions = True

    def construct(self,begin_date="jan 1",end_date="dec 31",group_payee=False,group_memo=False,account_id=None,account=None):
        self.begin_date = sanitized_date(begin_date)
        self.end_date = sanitized_date(end_date)
        self.group_payee = group_payee
        self.group_memo = group_memo
        self.account_obj = primaryKeyReferral(self, Accounts, id=account_id, name=account)

    def data(self):
        s = self.session().__class__()
        if self.group_payee and self.group_memo:
            q=s.query(func.sum(Splits.sum).label("sum"),Transactions.payee,Transactions.memo).join(Transactions).join(Accounts)
        elif not self.group_payee and self.group_memo:
            q=s.query(func.sum(Splits.sum).label("sum"),Transactions.memo).join(Transactions).join(Accounts)
        elif self.group_payee and not self.group_memo:
            q=s.query(func.sum(Splits.sum).label("sum"),Transactions.payee).join(Transactions).join(Accounts)
        else:
            q=s.query(Splits.sum,Transactions.tid.label("tran_id"),Transactions.date,Transactions.reference,Transactions.payee,Transactions.memo).join(Transactions).join(Accounts)
        if self.account_obj is not None:
            q = q.filter(Accounts.id==self.account_obj.id)
        if self.begin_date is not None:
            q=q.filter(Transactions.date>=self.begin_date)
        if self.end_date is not None:
            q=q.filter(Transactions.date<=self.end_date)
        if self.group_payee and self.group_memo:
            q=q.group_by(Transactions.payee,Transactions.memo)
        elif not self.group_payee and self.group_memo:
            q=q.group_by(Transactions.memo)
        elif self.group_payee and not self.group_memo:
            q=q.group_by(Transactions.payee)
        else:
            q = q.order_by(Transactions.date)
        lines = q.all()
        for p in lines:
            dc_object(p,"sum")
        s.close()
        return lines

    def columns(self):
        if self.group_payee and self.group_memo:
            return [ModelColumn("payee",str,label="Payee"),
                ModelColumn("memo",str,label="Memo"),
                ModelColumn("debit",decimal.Decimal,label="Debit"),
                ModelColumn("credit",decimal.Decimal,label="Crebit")]
        elif not self.group_payee and self.group_memo:
            return [ModelColumn("memo",str,label="Memo"),
                ModelColumn("debit",decimal.Decimal,label="Debit"),
                ModelColumn("credit",decimal.Decimal,label="Crebit")]
        elif self.group_payee and not self.group_memo:
            return [ModelColumn("payee",str,label="Payee"),
                ModelColumn("debit",decimal.Decimal,label="Debit"),
                ModelColumn("credit",decimal.Decimal,label="Crebit")]
        else:
            return [ModelColumn("date",datetime.date,label="Date"),
                ModelColumn("reference",str,label="Reference"),
                ModelColumn("payee",str,label="Payee"),
                ModelColumn("memo",str,label="Memo"),
                ModelColumn("debit",decimal.Decimal,label="Debit"),
                ModelColumn("credit",decimal.Decimal,label="Crebit")]

    def tableExtensionId(self):
        if self.group_payee and self.group_memo:
            return "DataGroupedFull"
        elif not self.group_payee and self.group_memo:
            return "DataGroupedMemo"
        elif self.group_payee and not self.group_memo:
            return "DataGroupedPayee"
        else:
            return "DataDetail"

    def objectConverter(self):
        return lambda x: x.tran_id

class TransactionList(PyHaccReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource(datetime.date(2011,3,31))
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,TransactionList,type_='Asset', begin_date='jan 1 2011', end_date='dec 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.date:%Y.%m.%d} {0.payee:15s} {0.memo:15s} {0.sum:>8.2f}".format(x)
    2011.01.02 ACME Inc        Payroll           400.00
    2011.01.09 ACME Inc        Payroll           400.00
    2011.01.16 ACME Inc        Payroll           400.00
    2011.01.23 ACME Inc        Payroll           400.00
    2011.01.30 ACME Inc        Payroll           400.00
    2011.01.30 Central Bank    Mortgage         -550.00
    2011.02.06 ACME Inc        Payroll           400.00
    2011.02.13 ACME Inc        Payroll           400.00
    2011.02.20 ACME Inc        Payroll           400.00
    2011.02.27 ACME Inc        Payroll           400.00
    2011.03.01 Central Bank    Mortgage         -550.00
    2011.03.06 ACME Inc        Payroll           400.00
    2011.03.13 ACME Inc        Payroll           400.00
    2011.03.20 ACME Inc        Payroll           400.00
    2011.03.27 ACME Inc        Payroll           400.00
    2011.03.31 Central Bank    Mortgage         -550.00
    2011.03.31 Giant           Groceries         -11.24
    2011.04.03 ACME Inc        Payroll           400.00
    >>> rpt = sessionedObjectInit(s,TransactionList, begin_date='mar 1 2011', end_date='dec 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.date:%Y.%m.%d} {0.account:15s} {0.payee:15s} {0.memo:15s} {0.sum:>8.2f}".format(x)
    2011.03.01 Checking        Central Bank    Mortgage         -550.00
    2011.03.01 House           Central Bank    Mortgage          550.00
    2011.03.06 Checking        ACME Inc        Payroll           400.00
    2011.03.06 Day Job         ACME Inc        Payroll          -400.00
    2011.03.13 Checking        ACME Inc        Payroll           400.00
    2011.03.13 Day Job         ACME Inc        Payroll          -400.00
    2011.03.20 Checking        ACME Inc        Payroll           400.00
    2011.03.20 Day Job         ACME Inc        Payroll          -400.00
    2011.03.27 Checking        ACME Inc        Payroll           400.00
    2011.03.27 Day Job         ACME Inc        Payroll          -400.00
    2011.03.31 Checking        Central Bank    Mortgage         -550.00
    2011.03.31 House           Central Bank    Mortgage          550.00
    2011.03.31 Cash            Giant           Groceries         -11.24
    2011.03.31 Groceries       Giant           Groceries          11.24
    2011.04.03 Checking        ACME Inc        Payroll           400.00
    2011.04.03 Day Job         ACME Inc        Payroll          -400.00
    """
    name="Transaction Lists"
    type_name = AccountTypeReferral("Account Type","type_obj")
    journal = JournalReferral("Journal","journal_obj")
    begin_date = UserAttr(Nullable(datetime.date), "Begin Date")
    end_date = UserAttr(Nullable(datetime.date), "End Date")
    prompt_order = ("begin_date","end_date","journal","type_name")
    entity_class = TransactionEntity

    def construct(self,begin_date="jan 1",end_date="dec 31",journal_id=None,journal=None,type_id=None,type_=None):
        self.begin_date = sanitized_date(begin_date)
        self.end_date = sanitized_date(end_date)
        self.journal_obj = primaryKeyReferral(self, Journals, id=journal_id, name=journal)
        self.type_obj = primaryKeyReferral(self, AccountTypes, id=type_id, name=type_)

    def data(self):
        s = self.session().__class__()
        q=s.query(Splits.sum, Transactions.tid, Transactions.date, Transactions.reference, Transactions.payee, Transactions.memo, Accounts.name.label("account")).join(Transactions).join(Accounts)
        if self.journal_obj is not None:
            q = q.filter(Accounts.journal_id==self.journal_obj.id)
        if self.type_obj is not None:
            q = q.filter(Accounts.type_id==self.type_obj.id)
        if self.begin_date is not None:
            q=q.filter(Transactions.date>=self.begin_date)
        if self.end_date is not None:
            q=q.filter(Transactions.date<=self.end_date)
        q = q.order_by(Transactions.date, Transactions.payee)
        rows = q.all()
        for r in rows:
            dc_object(r,"sum")
        s.close()
        return rows

    def columns(self):
        return [ModelColumn("account",str,label="Account",width=20),
            ModelColumn("date",datetime.date,label="Date",width=15),
            ModelColumn("reference",str,label="Reference",width=12),
            ModelColumn("payee",str,label="Payee",width=40),
            ModelColumn("memo",str,label="Memo",width=40),
            ModelColumn("debit",decimal.Decimal,label="Debit",width=12),
            ModelColumn("credit",decimal.Decimal,label="Crebit",width=12)]

    def objectConverter(self):
        return lambda x: x.tid

    @property
    def page_size(self):
        return "landscape_letter"

    @property
    def report_title(self):
        my_title = "Transactions"
        if self.begin_date is not None and self.end_date is not None:
            my_title = "Transactions {0.begin_date:%x} to {0.end_date:%x}".format(self)
        elif self.begin_date is not None and self.end_date is None:
            my_title = "Transactions since {0.begin_date:%x}".format(self)
        elif self.begin_date is None and self.end_date is not None:
            my_title = "Transactions before {0.end_date:%x}".format(self)

        if self.type_obj is not None:
            my_title += " (Type {0.type_name})".format(self)
        return my_title

class ProfitAndLoss(AccountBalanceListReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource(datetime.date(2011,3,31))
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,ProfitAndLoss,begin_date='mar 1 2011', end_date='mar 31 2011')
    >>> for x in rpt.data():
    ...     print "{0.accounts_name:15s} {0.amount:>8.2f}".format(x)
    Day Job         -1600.00
    Groceries          11.24
    House            1100.00
    """
    name="Profit & Loss"
    title_shell = "{0.name} for {0.begin_date:%x}-{0.end_date:%x}"
    journal = JournalReferral("Journal","journal_obj")
    begin_date = UserAttr(datetime.date, "Begin Date")
    end_date = UserAttr(datetime.date, "End Date")
    prompt_order = ("begin_date","end_date","journal")

    def construct(self,begin_date="jan 1",end_date="dec 31",journal_id=None,journal=None):
        self.begin_date = sanitized_date(begin_date)
        self.end_date = sanitized_date(end_date)
        self.journal_obj = primaryKeyReferral(self, Journals, id=journal_id, name=journal)

    def data(self):
        s = self.session().__class__()
        # set up the main query
        if self.journal_obj is None:
            tranCriteria = expr.and_(Transactions.date>=self.begin_date,Transactions.date<=self.end_date)
        else:
            tranCriteria = expr.and_(Transactions.date>=self.begin_date,Transactions.date<=self.end_date,Accounts.journal_id==self.journal_obj.id)
        t=s.query(
                Accounts.id.label("accounts_id"),
                Accounts.name.label("accounts_name"),
                AccountTypes.id.label("accounttypes_id"),
                AccountTypes.name.label("accounttypes_name"),
                func.sum(Splits.sum).label("amount")
                ).join(Splits).join(AccountTypes).join(Transactions) \
                    .group_by(Accounts.id,Accounts.name,AccountTypes.id,AccountTypes.name,AccountTypes.sort) \
                    .order_by(AccountTypes.sort, Accounts.name) \
                    .filter(expr.not_(AccountTypes.balance_sheet)) \
                    .filter(tranCriteria)

        d = t.all()
        s.close()
        return self.post_process_data(d)

def intervals(end,count,length):
    year, month, day = end.year, end.month, end.day
    if end == month_end(year,month):
        interval_final = year*12+month-1
        for i in range(count):
            begin = interval_final - (count-i)*length + 1
            end = interval_final - (count-i-1)*length
            year1,month1=begin / 12, (begin % 12)+1
            year2,month2=end / 12, (end % 12)+1
            yield (datetime.date(year1,month1,1),month_end(year2,month2))
    else:
        interval_final = year*12+month-1
        for i in range(count):
            begin = interval_final - (count-i)*length
            end = interval_final - (count-i-1)*length
            year1,month1=begin / 12, (begin % 12)+1
            year2,month2=end / 12, (end % 12)+1
            yield (month_safe_day(year1,month1,day)+datetime.timedelta(1),month_safe_day(year2,month2,day))

class IntervalPL(PyHaccReport):
    """
    >>> app = qtapp()
    >>> from pyhacc import MemorySource
    >>> Session = MemorySource(datetime.date(2011,3,31))
    >>> s = Session()
    >>> rpt = sessionedObjectInit(s,IntervalPL,end_date='jun 30 2011', interval_length = 3)
    >>> for x in rpt.data():
    ...     print "{0.accounts_name:15s} {0.amount0:>8.2f} {0.amount1:>8.2f} {0.amount2:>8.2f}".format(x)
    Day Job         -5200.00 -5200.00  -400.00
    Groceries           0.00    11.24     0.00
    House            2200.00  1650.00     0.00
    """
    name="Interval P&L"
    journal = JournalReferral("Journal","journal_obj")
    interval_length = UserAttr(int,"Interval Length")
    interval_count = UserAttr(int,"Interval Count")
    end_date = UserAttr(datetime.date, "End Date")
    prompt_order = ("end_date","interval_length", "interval_count","journal")
    refresh_model_dimensions = True

    def construct(self,end_date="dec 31",interval_length=6,interval_count=3,journal_id=None,journal=None):
        self.end_date = sanitized_date(end_date)
        self.interval_length = int(interval_length)
        self.interval_count = int(interval_count)
        self.journal_obj = primaryKeyReferral(self, Journals, id=journal_id, name=journal)

    def data(self):
        s = self.session().__class__()
        subs = []
        dates = intervals(self.end_date,self.interval_count,self.interval_length)
        for d1,d2 in dates:
            # set up the main query
            if self.journal_obj is None:
                tranCriteria = expr.and_(Transactions.date>=d1,Transactions.date<=d2)
            else:
                tranCriteria = expr.and_(Transactions.date>=d1,Transactions.date<=d2,Accounts.journal_id==self.journal_obj.id)
            q = s.query(
                    Accounts.id.label("account_id"),
                    func.sum(Splits.sum).label("sum")).join(Splits).join(AccountTypes).join(Transactions) \
                    .filter(tranCriteria).filter(expr.not_(AccountTypes.balance_sheet)).group_by(Accounts.id)
            #print q.all()
            subs.append(q.subquery())
        cols = [Accounts.id.label("id"),
                Accounts.name.label("accounts_name"),
                Accounts.description.label("accounts_description"),
                AccountTypes.id.label("accounttypes_id"),
                AccountTypes.sort.label("accounttypes_sort"),
                func.max(AccountTypes.name).label("accounttypes_name")]
        for q in range(len(subs)):
            cols.append(func.sum(subs[q].c.sum).label("amount{0}".format(q)))
        #print cols

        t=s.query(*tuple(cols)).join(AccountTypes)
        for q in subs:
            t=t.outerjoin((q,Accounts.id==q.c.account_id))
        t = t.filter(expr.not_(AccountTypes.balance_sheet)) \
                .group_by(Accounts.id, Accounts.name, Accounts.description, AccountTypes.id, AccountTypes.sort) \
                .order_by(AccountTypes.sort, Accounts.name)
        #print t

        # post-process a bit
        lines = t.all()
        lines.sort(key=lambda x: (x.accounttypes_sort, x.accounts_name))
        for l in lines:
            for i in range(self.interval_count):
                if getattr(l,"amount{0}".format(i)) is None:
                    setattr(l,"amount{0}".format(i),decimal.Decimal('0.00'))
        def all_zeros(l):
            for i in range(self.interval_count):
                if getattr(l,"amount{0}".format(i)) != decimal.Decimal():
                    return False
            return True
        return [l for l in lines if not all_zeros(l)] 

    def columns(self):
        cols = [ModelColumn("accounttypes_name",str,label="Account Type"),
            ModelColumn("accounts_name",str,label="Account"),
            ModelColumn("accounts_description",str,label="Description")]
        dates = list(intervals(self.end_date,self.interval_count,self.interval_length))
        for i in range(self.interval_count):
            d1,d2 = dates[i]
            cols.append(ModelColumn("amount{0}".format(i),decimal.Decimal,label="{0:%x}-{1:%x}".format(d1, d2)))
            #ModelColumn("debit",decimal.Decimal,label="Debit"),
            #ModelColumn("credit",decimal.Decimal,label="Crebit")]
        return cols

    def tableExtensionId(self):
        return "DataTable_{0}column".format(self.interval_count)

    @property
    def report_title(self):
        dates = list(intervals(self.end_date, self.interval_count, self.interval_length))
        return "{0.name} for {1:%x} - {2:%x}".format(self, dates[0][0], dates[-1][1])

    def geraldo(self, outfile, pagesize, **kwargs):
        from geraldo import Report, DetailBand, ObjectValue, Label, FIELD_ACTION_COUNT, FIELD_ACTION_SUM,  ReportGroup,  ReportBand, SystemField, BAND_WIDTH
        from geraldo.utils import cm
        from geraldo.generators import PDFGenerator
        from reportlab.lib.enums import TA_CENTER, TA_RIGHT
        
        if pagesize is None:
            pagesize = "landscape_letter"
        dates = list(intervals(self.end_date,self.interval_count,self.interval_length))

        col_contents = [ObjectValue(attribute_name='amount{0}'.format(i), 
                                display_format="%s", 
                                top=0, left=(i*4+8)*cm, 
                                style={'alignment': TA_RIGHT}) for i in range(self.interval_count)]

        col_footer = [ObjectValue(attribute_name='amount{0}'.format(i), 
                                action=FIELD_ACTION_SUM, 
                                display_format="%s", 
                                top=0, left=(i*4+8)*cm, 
                                style={'alignment': TA_RIGHT}) for i in range(self.interval_count)]

        col_header = [Label(text="{0:%x}".format(dates[i][1]), 
                                top=0, left=(i*4+10)*cm,
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 12}) for i in range(self.interval_count)]

        class GeraldoInterval(GeraldoTemplate(self, pagesize)):
            class band_detail(DetailBand):
                height=0.7*cm
                elements = [
                            ObjectValue(attribute_name='accounts_name', top=0, left=1*cm),
                            ObjectValue(attribute_name='accounts_description', top=0, left=4*cm)]\
                            + col_contents
            groups = [
                ReportGroup(attribute_name='accounttypes_name',
                    band_header=ReportBand(
                        height=0.7*cm,
                        elements=[
                            ObjectValue(attribute_name='accounttypes_name', left=0, top=0.1*cm,
                                #get_value=lambda instance: 'Superuser: ' + (instance.is_superuser and 'Yes' or 'No'),
                                style={'fontName': 'Helvetica-Bold', 'fontSize': 12})
                        ]+col_header
                        ,
                        borders={'bottom': True},
                    ),
                    band_footer=ReportBand(
                        height=0.7*cm,
                        elements=col_footer,
                        borders={'top': True},
                    ),
                )]
        
        bs = GeraldoInterval(queryset = self.data())
        bs.generate_by(PDFGenerator, filename=outfile)


report_classes = [JournalList,
                    AccountList,
                    BalanceSheet,
                    ProfitAndLoss,
                    IntervalPL,
                    TransactionsByAccount,
                    TransactionList]
