import web

db = web.database(dbn='sqlite',
        db='../create_auctionbase/AuctionBase' #TODO: add your SQLite database filename
    )

######################BEGIN HELPER METHODS######################

# Enforce foreign key constraints
# WARNING: DO NOT REMOVE THIS!
def enforceForeignKey():
    db.query('PRAGMA foreign_keys = ON')

# initiates a transaction on the database
def transaction():
    return db.transaction()
# Sample usage (in auctionbase.py):
#
# t = sqlitedb.transaction()
# try:
#     sqlitedb.query('[FIRST QUERY STATEMENT]')
#     sqlitedb.query('[SECOND QUERY STATEMENT]')
# except Exception as e:
#     t.rollback()
#     print str(e)
# else:
#     t.commit()
#
# check out http://webpy.org/cookbook/transactions for examples

# returns the current time from your database
def getTime():
    # TODO: update the query string to match
    # the correct column and table name in your database
    query_string = 'select time from CurrentTime'
    results = queryWithResult(query_string)
    print(results)
    # alternatively: return results[0]['currenttime']
    return results[0].Time
    #return results[0].currenttime # TODO: update this as well to match the
                                  # column name

# returns a single item specified by the Item's ID in the database
# Note: if the `result' list is empty (i.e. there are no items for a
# a given ID), this will throw an Exception!


def getItemById(item_id):
    # TODO: rewrite this method to catch the Exception in case `result' is empty
    query_string = 'select * from Items where item_ID = $itemID'
    result = query(query_string, {'itemID': item_id})
    return result[0]

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def query(query_string, vars = {}):
    (db.query(query_string, vars))

# wrapper method around web.py's db.query method
# check out http://webpy.org/cookbook/query for more info
def queryWithResult(query_string, vars={}):
    return list(db.query(query_string, vars))

#####################END HELPER METHODS#####################

#TODO: additional methods to interact with your database,
# e.g. to update the current time


def update_curTime(curTime, prevTime):
    query_string = 'update currentTime Set Time = $curTime where Time = $Time'
    query(query_string, {'Time': prevTime, 'curTime': curTime})
    # else:
    #         t.commit()
        # //
    # //except Exception as e:
    #         print str(e)

    # results = query(query_string, {'Time':prevTime, 'curTime':curTime})


def insertBid(item_id, user_id, price, cur_time):
    query_string = 'insert into BIDS values ($item_id, $user_id, $price, $cur_time)'
    query(query_string, {'item_id': item_id, 'user_id': user_id, 'price': price, 'cur_time': cur_time})

def checkItemID(item_id):
    query_string = 'SELECT * FROM items WHERE itemid = $item_id'
    results = queryWithResult(query_string, {'item_id': item_id})
    return len(results) == 1

def checkUserID(user_id):
    query_string = 'SELECT * FROM users where userid = $user_id'
    results = queryWithResult(query_string, {'user_id': user_id})
    return len(results) == 1