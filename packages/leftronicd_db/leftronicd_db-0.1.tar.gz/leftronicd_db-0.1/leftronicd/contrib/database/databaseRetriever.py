from sqlalchemy import create_engine, select, MetaData, Table, func 
import json

__lastauthor__ = 'henry@leftronic.com'
__company__ = 'Leftronic'


class DatabaseRetriever:
    DB_TYPE_TO_PREFIX_MAP = {
        'mysql'         : 'mysql://%s:%s@%s/%s',
        'postgresql'    : 'postgresql://',
        'oracle'        : 'oracle://',
        'mssql'         : 'mssql+pyodbc://%s:%s@%s/%s',
        'sqlite'        : 'sqlite:///%s',
    }
    def __init__(self, stream):
        self.stream = stream
        self.url = self.getDBUrl()
        self.engine = None
        if self.url:
            self.engine = create_engine(self.url, echo=True)

    def getConnectionObject(self):
        '''Based on the params provided return a database connection object.'''
        conn = self.engine.connect()
        return conn
        
    def getDBUrl(self):
        '''Generate a url from the auth params'''
        method = getattr(self, 'get%sUrl' % (self.stream.configs['engine'].capitalize()))
        url = method()
        return url
    
    def getColumns(self, table):
        columns = []
        for column in self.stream.configs['columns']:
            columns.append(table.c[column])
        return columns
        
    def getTable(self):
        meta = MetaData()
        table = Table(self.stream.configs['table'], meta, autoload=True, autoload_with=self.engine)
        return table
        
    def execute(self):
        result = []
        table = None
        if self.engine:
            conn = self.getConnectionObject()
            table = self.getTable()
            columns = self.getColumns(table)
            s = select(columns)
            if 'limit' in self.stream.configs:
                limit = self.stream.configs['limit']
                s = s.limit(limit)
                if 'window' in self.stream.configs and 'last' == self.stream.configs['window']:
                    countStmt = select([func.count(columns[0])])
                    count = conn.execute(countStmt).scalar()
                    s = s.offset(count-limit)
            if 'asc' in self.stream.configs:
                s = s.order_by(table.c[self.stream.configs['asc']].asc())
            elif 'desc' in self.stream.configs:
                s = s.order_by(table.c[self.stream.configs['desc']].desc())
            resultset = conn.execute(s)
            for row in resultset:
                result.append(list(row))
        return result
    
    def getSqliteUrl(self):
        url = self.DB_TYPE_TO_PREFIX_MAP[self.stream.configs['engine']] % (self.stream.configs['database'])
        return url
        
    def getMysqlUrl(self):
        if 'username' not in self.stream.configs:
            return None
        if 'password' not in self.stream.configs:
            return None
        if 'host' not in self.stream.configs:
            return None
        if 'database' not in self.stream.configs:
            return None
        host = self.stream.configs['host']
        if 'port' in self.stream.configs:
            host += ':' + str(self.stream.configs['port'])
        url = self.DB_TYPE_TO_PREFIX_MAP[self.stream.configs['engine']] % (self.stream.configs['username'], self.stream.configs['password'], host, self.stream.configs['database'])
        return url

    def getMssqlUrl(self):
        url = None
        if 'dsn' in self.stream.configs:
            if 'username' in self.stream.configs and 'password' in self.stream.configs:
                url = "mssql+pyodbc://%s:%s@%s" %(self.stream.configs['username'], self.stream.configs['password'], self.stream.configs['dsn'])
            else:
                url = "mssql+pyodbc://%s" % (self.stream.configs['dsn'])
        elif 'username' in self.stream.configs and 'password' in self.stream.configs and 'host' in self.stream.configs and 'database' in self.stream.configs:
            host = self.stream.configs['host']
            if 'port' in self.stream.configs:
                host += ':' + str(self.stream.configs['port'])
            url = self.DB_TYPE_TO_PREFIX_MAP[self.stream.configs['engine']] % (self.stream.configs['username'], self.stream.configs['password'], host, self.stream.configs['database'])
        return url
