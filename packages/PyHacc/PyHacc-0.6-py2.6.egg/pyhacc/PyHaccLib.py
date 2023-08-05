# -*- coding: utf-8 -*-
##############################################################################
#       Copyright (C) 2010, Joel B. Mohler <joel@kiwistrawberry.us>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#                  http://www.gnu.org/licenses/
##############################################################################
from PyHaccSchema import *
from sqlalchemy.orm import sessionmaker
import sqlalchemy.pool

pyhacc_version = '0.6'

def SessionSource(conn, create_level=0, demo_info = None):
    if conn == 'sqlite://':
        engine = create_engine(conn, poolclass=sqlalchemy.pool.StaticPool, connect_args={'check_same_thread':False})
    else:
        engine = create_engine(conn)
    metadata.bind = engine
    s = PBSessionMaker(bind=engine)
    if create_level > 0:
        metadata.create_all()
        InsertSystemRows(s)
        if create_level > 1:
            BuildDemoData(s, demo_info = demo_info)
    else:
        # execute a query to fling an exception on an unrecognized database
        # truly speaking, this is a merely a most rudimentary check, but it will prevent hooking up to obviously wrong or massively uninitialized data-sets.
        test = s()
        test.query(Options).count()
    return s

def MemorySource(end_date = None):
    return SessionSource('sqlite://', 2, {'end_date': end_date})

def visual_date(date):
    return date.strftime( "%Y.%m.%d" )

def month_end(year,month):
    if month == 12:
        date = datetime.date(year,12,31)
    else:
        date = datetime.date(year,month+1,1)-datetime.timedelta(1)
    return date

def month_safe_day(year,month,day):
    """
    >>> month_safe_day(2011,2,30)
    datetime.date(2011, 2, 28)
    >>> month_safe_day(2012,2,30)
    datetime.date(2012, 2, 29)
    >>> month_safe_day(2011,4,31)
    datetime.date(2011, 4, 30)
    >>> month_safe_day(2011,4,15)
    datetime.date(2011, 4, 15)
    >>> month_safe_day(2011,12,33)
    datetime.date(2011, 12, 31)
    """
    try:
        return datetime.date(year,month,day)
    except:
        if month == 12:
            return datetime.date(year+1,1,1)-datetime.timedelta(1)
        else:
            return datetime.date(year,month+1,1)-datetime.timedelta(1)

def prior_month_end(date):
    pme = datetime.date(date.year,date.month,1)
    return pme-datetime.timedelta(1)
