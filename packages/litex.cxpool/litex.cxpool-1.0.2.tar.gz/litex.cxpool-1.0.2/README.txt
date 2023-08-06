litex.cxpool - a SQLAlchemy pool with native Oracle session pooling
===================================================================

CxOracleSessionPool is a subclass of SQLAlchemy's NullPool, with functionality close
to QueuePool. It's major selling point is the ability to run in proxy authentication
mode. In this mode, the session pool is constructed with one set of credentials and
individual connections can by acquired from it, authenticated for a different user.

It's being used in Pyramid applications interfacing with an ERP system with all logic, 
auditing and security contained in Oracle DB stored procedures. 

Example usage:

>>> from litex.cxpool import CxOracleSessionPool
>>> def get_user():
...     return 'REAL_USER'

get_user is a callable returning login of a user we would like to connect as. 
To connect to db as currently authenticated user in Pyramid, this
function could look like the one below (prefix is used to find the right type of principals,
and exclude the system. ones e.g. system.Everyone):

>>> from pyramid.threadlocal import get_current_request
>>> from pyramid.interfaces import IAuthenticationPolicy
>>> prefix = 'example.'
>>> def get_user():
...     req = get_current_request()
...         auth = req.registry.queryUtility(IAuthenticationPolicy)
...         prc = [pr for pr in auth.effective_principals(req) if pr.startswith(prefix)]   
...         if prc:
...             return prc[0].split('.')[-1]
...         else:
...             return None

Having the user source, we can construct the pool:

>>> pool = CxOracleSessionPool(
...    'oracle://proxy_user:proxy_password@test_server/test', 
...    min_sessions=1, 
...    max_sessions=5, 
...    increment=1, 
...    user_source=get_user
... )

 * First parameter is a database URL with proxy user credentials.
 * min_sessions controls, how many sessions are constructed initially (in contrast to SA QueuePool this pool precreates sessions)
 * max_sessions sets the upper cap of constructed sessions count (think about it as QP pool_size + max_overflow)
 * increment sets how many sessions to create when current session count is too low (up to max_sessions)

To allow REAL_USER to connect to the db through PROXY_USER, one have to issue the following statement as DBA:

sql> alter user REAL_USER grant connect through PROXY_USER;

Having the pool ready, we can construct a SQLAlchemy engine

>>> from sqlalchemy import create_engine
>>> engine = create_engine('oracle://', pool=pool)

and use it as any other SA engine:

>>> conn = engine.connect()
>>> res = conn.execute('select user from dual')
<sqlalchemy.engine.base.ResultProxy object at 0x1670b50>
>>> res.fetchone()
(u'REAL_USER',)

Changes:
========
1.0.2
-----
 - SQLAlchemy 0.7 compatible

1.0.1
-----
 - namespace package specification
 - various packaging errors

1.0
---
 - initial release