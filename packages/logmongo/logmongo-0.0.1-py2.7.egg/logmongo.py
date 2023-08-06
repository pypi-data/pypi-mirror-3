from pymongo import Connection 
from pymongo.errors import CollectionInvalid, AutoReconnect

from datetime import datetime as DT
from socket import getfqdn
#from getpass import getuser

from prettyprint import pp

'''
What have we gained?

A new Logmongo object will:
 * gracefully create a named capped collection 
 * allow a max size to be specified

The read method:
 * returns a cursor object of all logs

The write method:
 * logs all passed keywords
 * adds current time to entry
 * adds fqhn to entry

The query method:
 * allows query access using keywords 
   example: log.query( tags='finance' )

The tail method:
 * print all entries that match query until killed
'''

class Logmongo( object ):
    def __init__( self, host='localhost', port=27017, 
            db='logs', collection='log', size=524288000 ):
            # size in bytes: default 500MB
        conn = Connection( host, port )

        self.DB = conn[db]
        try: # attempt to create capped collection
            self.LOG = self.DB.create_collection(
                collection,
                capped=True,
                size=size
            )
        except CollectionInvalid:
            # collection already exists, skipping
            self.LOG = self.DB[collection] 
        

    def write( self, record=None, **kwargs ):
        """Log all kwargs with timestamp to collection"""
        if record:
            record = dict( record.items() + kwargs.items() )
        else:
            record = kwargs

        record['date'] = DT.now()
        record['host'] = getfqdn()
        self.LOG.save( record )

    def read( self ):
        """return a cursor object of all logs"""
        return self.LOG.find()

    def query( self, query=None, **kwargs ):
        """return a cursor object of all logs that match query"""
        if query: return self.LOG.find( query )
        return self.LOG.find( kwargs )

    def tail( self, n=10, **kwargs ):    
        """print all entries that match query until killed"""
        from time import sleep

        count = self.LOG.count()
        nskip = count - n

        if nskip < 0: nskip = 0
      
        cursor = self.LOG.find( kwargs, tailable=True ).skip( nskip )

        while cursor.alive:
            try:
                entry = cursor.next()
                pp( entry ) 
            except StopIteration:
                sleep(1)

    def clear( self ):
        """Warning this is destructive and drops collection"""
        self.DB.drop_collection( self.LOG )


if __name__ == '__main__':
    pass
