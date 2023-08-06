# -*- encoding: UTF-8 -*-
# (c) 2011 Michał Węgrzynek, Litex
# for license see http://repoze.org/license.html
'''
A SqlAlchemy connection pool utilizing cx_Oracle's SessionPool object.
It's intended to be created independently and passed by pool keyword
argument to create_engine.
'''
import cx_Oracle as cx
from sqlalchemy.pool import Pool
from sqlalchemy.engine.url import make_url


class CxOracleSessionPool(Pool):
    
    _v_session_pool = None
    
    def __init__(
        self, url_string, min_sessions=5, max_sessions=20, increment=2,
        user_source=None, **kw
    ):
        self.url_string = url_string
        self.min_sessions = min_sessions
        self.max_sessions = max_sessions
        self.increment = increment
        
        if user_source is None:
            self.user_source = lambda: None
        else:
            self.user_source = user_source
                
        super(CxOracleSessionPool, self).__init__(self._connect, **kw)
    
    @property
    def session_pool(self):
        if not self._v_session_pool:
            url = make_url(self.url_string)            
            
            self._v_session_pool = cx.SessionPool(
                url.username,
                url.password,
                cx.makedsn(url.host, url.port if url.port else 1521, url.database),
                self.min_sessions,
                self.max_sessions,
                self.increment,
                threaded=True,
                homogeneous=False
            )
            
        return self._v_session_pool
    
    def _connect(self):                    
        username = self.user_source()
        if username:
            return self.session_pool.acquire(username)
        else:
            return self.session_pool.acquire()

    def _do_get(self):
        return self._create_connection()    
        
    def _do_return_conn(self, conn):
        self.session_pool.release(conn.connection)
        conn.close()     
        
    def recreate(self):    
        self.logger.info("Pool recreating")

        return CxOracleSessionPool(
            self.url_string, 
            self.min_sessions, 
            self.max_sessions, 
            self.increment,
            self.user_source,
            recycle=self._recycle,
            echo=self.echo,
            logging_name=self._orig_logging_name,
            use_threadlocal=self._use_threadlocal,
            _dispatch=self.dispatch
        )

    def dispose(self):
        self._v_session_pool = None
        self.logger.info('Pool disposed')
        
    def status(self):
        return 'CxOracleSessionPool id=%s max sessions=%d current session count=%d' % (
            id(self),
            self.max_sessions,
            self.session_pool.busy
        )
    
    
  