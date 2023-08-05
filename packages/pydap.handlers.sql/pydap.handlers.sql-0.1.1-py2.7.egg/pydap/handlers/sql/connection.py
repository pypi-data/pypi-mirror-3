import urllib

from pydap.model import *


def get_connection(dsn):
    protocol, location = dsn.split('://', 2)

    conns = {
            'sqlite': _conn_sqlite,
            'postgresql': _conn_pgsql,
            'postgres': _conn_pgsql,
            'psql': _conn_pgsql,
            'pgsql': _conn_pgsql,
            'mysql': _conn_mysql,
            'oracle': _conn_oracle,
            'mssql': _conn_mssql,
            'odbc': _conn_odbc,
            }
    return conns[protocol](location)


def _conn_sqlite(location):
    try:
        import sqlite3 as sqlite
    except ImportError:
        from pysqlite2 import dbapi2 as sqlite

    conn = sqlite.connect(location, detect_types=sqlite.PARSE_DECLTYPES|sqlite.PARSE_COLNAMES)
    return conn


def _conn_pgsql(location):
    from psycopg2 import connect, STRING, DATETIME, NUMBER

    user, passwd, host, port, dbname = split_dsn(location)
    conn_str = [('dbname', dbname)]
    if host: conn_str.append(('host', host))
    if port: conn_str.append(('port', str(port)))
    if user: conn_str.append(('user', user))
    if passwd: conn_str.append(('password', passwd))
    conn_str = ['='.join(t) for t in conn_str]
    conn_str = ' '.join(conn_str)

    conn = connect(conn_str)
    return conn


def _conn_mysql(location):
    from MySQLdb import connect, STRING, DATETIME, NUMBER

    user, passwd, host, port, db = split_dsn(location)
    kwargs = {'db': db}
    if host: kwargs['host'] = host
    if port: kwargs['port'] = port
    if user: kwargs['user'] = user
    if passwd: kwargs['passwd'] = passwd

    conn = connect(**kwargs)
    return conn


def _conn_oracle(location):
    from cx_Oracle import connect, STRING, DATETIME, NUMBER, makedsn

    user, passwd, host, port, db = split_dsn(location)
    kwargs = {'dsn': makedsn(host, port, db)}
    if user: kwargs['user'] = user
    if passwd: kwargs['password'] = passwd

    conn = connect(**kwargs)
    return conn


def _conn_mssql(location):
    from adodbapi import connect, STRING, DATETIME, NUMBER

    user, passwd, host, port, db = split_dsn(location)
    conn_str = [('Driver', '{SQL Server}'),
                ('Database', db)]
    if host: conn_str.append(('Server', host))
    if port: conn_str.append(('Port', str(port)))
    if user: conn_str.append(('Uid', user))
    if passwd: conn_str.append(('Pwd', passwd))
    conn_str = ['='.join(t) for t in conn_str]
    conn_str = ';'.join(conn_str)

    conn = connect(conn_str)
    return conn


def _conn_odbc(conn_str):
    try:
        from ceODBC import connect, STRING, DATETIME, NUMBER
    except ImportError:
        from pyodbc import connect, STRING, DATETIME, NUMBER

    conn = connect(conn_str)
    return conn


def split_dsn(location):
    """
    Split DSN into user, password, host, port and dbname.
    
        >>> print split_dsn('user:pass@host:80/db')
        ('user', 'pass', 'host', '80', 'db')
        >>> print split_dsn('host/db')
        (None, None, 'host', None, 'db')
        >>> print split_dsn('user@host/db')
        ('user', None, 'host', None, 'db')
        >>> print split_dsn('user:pass@host/db')
        ('user', 'pass', 'host', None, 'db')

    """
    user, host = urllib.splituser(location)
    if user:
        user, password = urllib.splitpasswd(user)
    else:
        password = None

    host, dbname = urllib.splithost('//' + host)
    if dbname.startswith('/'): dbname = dbname[1:]
    host, port = urllib.splitport(host)

    return user, password, host, port, dbname

