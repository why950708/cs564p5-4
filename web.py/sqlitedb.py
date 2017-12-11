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
    query_string = 'select * from Items where ItemID = $itemID'
    result = query(query_string, {'itemID': item_id})
    print "///////// ",result
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

def getBuyPrice(item_id):
    query_string = 'SELECT Buy_Price from items where itemid = $item_id'
    results = queryWithResult(query_string, {'item_id': item_id})
    return results[0].Buy_Price

def getCurrently(item_id):
    query_string = 'SELECT Currently from items where itemid = $item_id'
    results = queryWithResult(query_string, {'item_id': item_id})
    return results[0].Currently

#true if auction has ended
def hasAuctionEnded(item_id):
    if hasAuctionEndedSQLOnly(item_id):
        return True
    if getCurrently(item_id) >= getBuyPrice(item_id) and getBuyPrice(item_id) is not None:
        return True
    return False

#returns false if auction has not ended, true if auction has ended
def hasAuctionEndedSQLOnly(item_id):
    query_string = 'SELECT COUNT(*) FROM CurrentTime, items WHERE itemid=$item_id AND time < items.ends;'
    results = queryWithResult(query_string, {'item_id': item_id})
    if results is not None:
        return False
    return True

#returns true if auction has started, false if auction has not started
def hasAuctionStartedSQLOnly(item_id):
    query_string = 'SELECT COUNT(*) FROM CurrentTime, items WHERE itemid=$item_id AND time > items.started;'
    results = queryWithResult(query_string, {'item_id': item_id})
    if results is not None:
        return True
    return False

# i don't think this is used
def getAuctionEndTime(item_id):
    query_string = 'SELECT Ends from items where itemid = $item_id'
    results = queryWithResult(query_string, {'item_id': item_id})
    return results[0].Ends

## returns true if it is a valid bid, false otherwise
def checkBidBuyPrice(bid, item_id):
    if getBuyPrice(item_id) is None:
        return True
    if bid > getBuyPrice(item_id) and getCurrently(item_id) >= getBuyPrice(item_id):
        return False
    return True

# returns all item properties given an item id
def getItemReWrite(item_id):
    query_string = 'SELECT * from items where itemid = $item_id'
    result = queryWithResult(query_string, {'item_id':item_id})
    return result[0]

#returns all item categories given item id
def getItemCategories(item_id):
    query_string = 'SELECT * from Categories where itemid = $item_id'
    result = queryWithResult(query_string, {'item_id':item_id})
    return result[0]

def getBids(item_id):
    query_string = 'select userid, amount, time from bids where itemid = $item_id'
    result = queryWithResult(query_string, {'item_id':item_id})
    return result

#returns username of winning bidder if auction has ended or "No Winning Bidder" if there are no bids
def getWinningBidder(item_id):
    #check if auction has ended
    if hasAuctionEnded(item_id):
        query_string = 'select userid from bids where itemid = $item_id ORDER BY amount DESC limit 1'
        result = queryWithResult(query_string, {'item_id':item_id})
        if result is None:
            return "No Winning Bidder"
        else:
            returnVar = "Winning Bidder is"
            returnVar += result[0].UserID
            return returnVar
    else:
        return None