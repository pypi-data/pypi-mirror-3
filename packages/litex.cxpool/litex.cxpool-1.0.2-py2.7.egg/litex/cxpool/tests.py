# -*- encoding: UTF-8 -*-
import os


from nose.tools import eq_, ok_, assert_raises
from cx_Oracle import DatabaseError
from sqlalchemy import create_engine


DSN = os.environ.get('CX_DSN', 'oracle://test_user:test_password@test_server/test')
CONNECT_USER = os.environ.get('CX_CONNECT_USER', 'TEST_USER')
PROXY_USER = os.environ.get('CX_PROXY_USER', 'PROXY_USER')


def test_creation():
    from litex.cxpool import CxOracleSessionPool
    pool = CxOracleSessionPool(DSN, 1, 5, 1)
    
    new_pool = pool.recreate()
    eq_(pool.url_string, new_pool.url_string)
    eq_(pool.min_sessions, new_pool.min_sessions)
    eq_(pool.max_sessions, new_pool.max_sessions)
    eq_(pool.increment, new_pool.increment)
    
    
def test_checkout_and_status():
    from litex.cxpool import CxOracleSessionPool    
    
    pool = CxOracleSessionPool(DSN, 1, 3, 1)
    engine = create_engine('oracle://', pool=pool)
    
    conn_1 = engine.connect()
    eq_(pool.session_pool.busy, 1)
    
    conn_2 = engine.connect()
    eq_(pool.session_pool.busy, 2)
    
    conn_3 = engine.connect()
    eq_(pool.session_pool.busy, 3)
    
    assert_raises(DatabaseError, lambda: engine.connect())
    eq_(pool.session_pool.busy, 3)
    
    status = pool.status()
    ok_('CxOracleSessionPool' in status)
    ok_('max sessions=3' in status)
    ok_('current session count=3' in status)
    
    del conn_3
    eq_(pool.session_pool.busy, 2)


def test_proxy_auth():
    from litex.cxpool import CxOracleSessionPool    
    def user_src():
        return PROXY_USER
    
    pool = CxOracleSessionPool(DSN, 1, 3, 1)
    engine = create_engine('oracle://', pool=pool)
    
    conn_1 = engine.connect()
    res = conn_1.execute('SELECT USER FROM DUAL')
    
    usr = res.first()['user']
    eq_(usr, CONNECT_USER)
    
    pool = CxOracleSessionPool(DSN, 1, 3, 1, user_source=user_src)
    engine = create_engine('oracle://', pool=pool)
    
    conn_1 = engine.connect()
    res = conn_1.execute('SELECT USER FROM DUAL')
    
    usr = res.first()['user']
    eq_(usr, PROXY_USER)
    

def test_dispose():
    from litex.cxpool import CxOracleSessionPool
    pool = CxOracleSessionPool(DSN, 1, 3, 1)
    
    pool.dispose()