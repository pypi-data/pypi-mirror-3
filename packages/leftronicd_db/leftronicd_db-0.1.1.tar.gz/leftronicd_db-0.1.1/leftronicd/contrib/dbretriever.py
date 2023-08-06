from twisted.python import log
from twisted.internet import defer
from database.databaseRetriever import DatabaseRetriever

class Stream(object):
    pass

def get_page(handler, *args, **kwargs):
    deferred = Deferred()
    def callback(data):
        output = h
        deferred.callback(output)
    return deferred

# def execute_db_retriever(engine, database, table, columns, **kwargs):
def execute_db_retriever(engine, database, **kwargs):
    log.msg("Get db data is called with %s:%s" % (engine, database))
    def callback():
        headerRow = ['name', 'city', 'country']
        dataRows = [ ['Lionel', 'Rosario', 'Argentina'], ['Andres', 'Albacete', 'Spain']]
        stream = Stream()
        stream.configs = dict(kwargs)
        stream.configs['engine'] = engine
        stream.configs['database'] = database
        db = DatabaseRetriever(stream)
        dataRows = db.execute()
        result = { 'headerRow' : stream.configs['columns'], 'dataRows' : dataRows }
        return result
    return defer.execute(callback)
    