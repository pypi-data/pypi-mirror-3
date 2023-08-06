from pymongo import Connection 
from pymongo.collection import Collection 
from pymongo.errors import CollectionInvalid, AutoReconnect

from datetime import datetime as DT
from socket import gethostname
#from getpass import getuser

from prettyprint import pp

'''
What have we gained?

A new Logmongo object will:
 * gracefully create a named capped collection 
 * allow a max size to be specified

The write method:
 * logs all passed keywords
 * adds current time to entry
 * adds hostname to entry

The query method:
 * allows query access using keywords 
   example: log.query( tags='finance' )

The tail method:
 * print all entries that match query until killed
'''
class Logmongo( Collection ):
    def __init__( self, name, db='logs',
            size=524288000, host='localhost', port=27017, ):

        database = Connection( host, port )[db]

        try: # attempt to create capped collection
            database.create_collection(
                name,
                capped=True,
                size=size
            )
        except CollectionInvalid: # collection exists
            pass
        
        # run the super parent's init!
        super( Logmongo, self ).__init__( database, name )

    def write( self, record=None, **kwargs ):
        """Log all kwargs with timestamp to collection"""
        if record:
            record = dict( record.items() + kwargs.items() )
        else:
            record = kwargs

        record['date'] = DT.now()
        record['host'] = gethostname()
        self.save( record )

    def query( self, **kwargs ):
        """just like find, but accepts kwargs for query"""
        return self.find( kwargs )

    def tail( self, query={}, n=10 ):    
        """print all entries that match query until killed"""
        from time import sleep

        nskip = self.count() - n

        if nskip < 0: nskip = 0
      
        cursor = self.find( query, tailable=True ).skip( nskip )

        while cursor.alive:
            try:
                entry = cursor.next()
                pp( entry ) 
            except StopIteration:
                sleep(1)

    def update( self ):
        """logs should not be updated"""
        pass

    def remove( self ):
        """logs should not be removed"""
        """I might hack this and make it set an archive 'bit' """
        pass


if __name__ == '__main__':
    # create a log object
    log = Logmongo('20120713')

    # write some log records
    log.write( carter="I didn't did it." )
    log.write( dad="are you sure?" )
    log.write( carter="I didn't did it!" )
    
    # print logs forever until killed
    #log.tail() 

    # clear the log collection
    # log.drop()

    # print all log records
    for record in log.find(): print record

    #print log count
    print log.count()
