#!/usr/bin/env python

import sys; sys.path.insert(0, 'lib') # this line is necessary for the rest
import os                             # of the imports to work!

import web
import sqlitedb
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

###########################################################################################
##########################DO NOT CHANGE ANYTHING ABOVE THIS LINE!##########################
###########################################################################################

######################BEGIN HELPER METHODS######################

# helper method to convert times from database (which will return a string)
# into datetime objects. This will allow you to compare times correctly (using
# ==, !=, <, >, etc.) instead of lexicographically as strings.

# Sample use:
# current_time = string_to_time(sqlitedb.getTime())

def string_to_time(date_str):
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

# helper method to render a template in the templates/ directory
#
# `template_name': name of template file to render
#
# `**context': a dictionary of variable names mapped to values
# that is passed to Jinja2's templating engine
#
# See curr_time's `GET' method for sample usage
#
# WARNING: DO NOT CHANGE THIS METHOD
def render_template(template_name, **context):
    extensions = context.pop('extensions', [])
    globals = context.pop('globals', {})

    jinja_env = Environment(autoescape=True,
            loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
            extensions=extensions,
            )
    jinja_env.globals.update(globals)

    web.header('Content-Type','text/html; charset=utf-8', unique=True)

    return jinja_env.get_template(template_name).render(context)

#####################END HELPER METHODS#####################

urls = ('/currtime', 'curr_time',
        '/selecttime', 'select_time',
        '/add_bid', 'add_bid',
        '/search', 'search',
        '/single_item_view', 'single_item_view',
        '/single_item','single_item',
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )

class single_item:
    def GET(self):
        param = web.input()
        if (len(param)==0):
            return render_template('single_item_view.html')
        id = param.Id
        item = sqlitedb.getItemById(id)
        if (not item):
            update_message="No Such Item"
            return render_template('single_item_view.html', message=update_message)

        # get stuff from items table (category, item, description, etc)
        result = sqlitedb.getItemReWrite(id)

        # get categories of item
        categories = sqlitedb.getItemCategories(id)

        # figure out if the auction is closed or open
        auctionMessage = "Open"
        winning_bidder = None
        if not sqlitedb.hasAuctionStartedSQLOnly(id):
            auctionMessage = "Closed"
        if sqlitedb.hasAuctionEnded(id):
            auctionMessage = "Closed"
            if sqlitedb.getWinningBidder(id) is not None:
                winning_bidder = sqlitedb.getWinningBidder(id)

        bids = sqlitedb.getBids(id)
        if (not bids):
            allBids=[]
            if winning_bidder is not None:
                return render_template('single_item_view.html', results=result, categories=categories.Category,
                                       auctionMessage=auctionMessage,  winningBidder=winning_bidder)
            return render_template('single_item_view.html', results=result, categories=categories.Category,
                                   auctionMessage=auctionMessage,)
        else:
            allBids = bids
            print bids[0]['UserID']
            if winning_bidder is not None:
                return render_template('single_item_view.html', results=result, categories=categories.Category,
                                       auctionMessage=auctionMessage, allBids=bids, winningBidder=winning_bidder)
            return render_template('single_item_view.html', results=result, categories=categories.Category,
                                   auctionMessage=auctionMessage, allBids=bids, )





class search:
    def GET(self):
        return render_template('search.html')
    def POST(self):
        post_params = web.input()
        print post_params
        
        params = [  post_params['itemID'],
                    post_params['minPrice'],
                    post_params['maxPrice'],
                    post_params['userID'],
                    post_params['category'],
                    post_params['description'],
                    post_params['status']
                ] 

        if len(post_params['description']) != 0:
            params[5] = '%' + params[5] + '%'
        
        query = "Select I.ItemID, Name, Currently, Buy_Price, Started, Ends From Items as I"
        
        
        queries= [  "I.ItemID = $itemID",
                    "currently >= $minPrice",
                    "currently <= $maxPrice",
                    "Seller_UserID = $userID",
                    "C.ItemID == I.ItemID and category == $category",
                    "description LIKE $description"
                ]
        if params[6] == 'open':
            queries.append("Ends > time")
            query += ", CurrentTime"
        elif params[6] == 'close':
            queries.append("Ends < time")
            query += ", CurrentTime"
        elif params[6] == 'notStarted':
            queries.append("Started > time")
            query += ", CurrentTime"
        
        if len(params[4]) != 0:
            query += ", Categories as C"
        
        
        #TODO add in function call for status check
        
        first = True
        for x in range(0,len(queries)):
            if len(params[x]) is not 0:
                if first is True:
                        query += " where " + queries[x]
                        first = False
                else:
                    query += " and " + queries[x]

        result = sqlitedb.queryWithResult(query, {  'itemID': params[0], 
                                                    'minPrice': params[1],
                                                    'maxPrice': params[2],
                                                    'userID': params[3],
                                                    'category': params[4],
                                                    'description': params[5]
                                                    })

        #for result 
        return render_template('search.html', search_result=result)
        

class add_bid:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        return render_template('add_bid.html')
    def POST(self):
        print web.input()
        post_params = web.input()
        itemID = post_params['itemID']
        price = post_params['price']
        userID = post_params['userID']
        if not sqlitedb.checkItemID(itemID):
            update_message = 'ItemID is not found'
            return render_template('add_bid.html', message=update_message) 
        if not sqlitedb.checkUserID(userID):
            update_message = "UserID is not found"
            return render_template('add_bid.html', message=update_message)
        ''' if not sqlitedb.checkBidBuyPrice(price, itemID):
            update_message = 'Buy Price has already been exceeded'
            return render_template('add_bid.html', message=update_message) '''
        t = sqlitedb.transaction()
        if sqlitedb.hasAuctionEnded(itemID):
            update_message = 'Auction has ended'
        try:
            current_time = sqlitedb.getTime()
            int(itemID)
            #if isinstance(itemID, int):
            update_message = 'Bid set on item:%s at $%s' \
                        ' at %s' % ((itemID), (price), (current_time))
            sqlitedb.insertBid(itemID, userID, price, current_time)
        except Exception as e:
            t.rollback()
            print str(e)
            #update_message = str(e)
            update_message = "Please check your input"
            result = False
        else:
            result = True
            t.commit()
        ''' try:
            current_time = sqlitedb.getTime()
            int(itemID)
            #if isinstance(itemID, int):
            update_message = 'Bid set on item:%s at $%s' \
                        ' at %s' % ((itemID), (price), (current_time))
            sqlitedb.insertBid(itemID, userID, price, current_time)
            #else:
            #    raise Exception('Error: ItemID was not an int')
        except Exception as e:
            print str(e)
            update_message = str(e) '''

        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('add_bid.html', message=update_message, add_result=result)



class curr_time:
    # A simple GET request, to '/currtime'
    #
    # Notice that we pass in `current_time' to our `render_template' call
    # in order to have its value displayed on the web page
    def GET(self):
        current_time = sqlitedb.getTime()
        return render_template('curr_time.html', time = current_time)

class select_time:
    # Aanother GET request, this time to the URL '/selecttime'
    def GET(self):
        return render_template('select_time.html')

    # A POST request
    #
    # You can fetch the parameters passed to the URL
    # by calling `web.input()' for **both** POST requests
    # and GET requests
    def POST(self):
        post_params = web.input()
        print web.input()
        MM = post_params['MM']
        dd = post_params['dd']
        yyyy = post_params['yyyy']
        HH = post_params['HH']
        mm = post_params['mm']
        ss = post_params['ss'];
        enter_name = post_params['entername']
        selected_time = '%s-%s-%s %s:%s:%s' % (yyyy, MM, dd, HH, mm, ss)
        update_message = '(Hello, %s. Previously selected time was: %s.)' % (enter_name, selected_time)
        try:
            sqlitedb.update_curTime(selected_time, sqlitedb.getTime())
        except Exception as e:
            update_message = 'Error occured, please select a new time'
            print str(e)
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('select_time.html', message=update_message)

class single_item_view:
    def GET(self):
        return render_template('single_item_view.html')
    def POST(self):
        #grab parameters from post
        post_params = web.input()
        item_id = post_params['itemID']

        #check if itemID is valid, if not, let user know
        if not sqlitedb.checkItemID(item_id):
            message = "Item was not found"
            return render_template('single_item_view.html', message=message)
        #get stuff from items table (category, item, description, etc)
        result = sqlitedb.getItemReWrite(item_id)
        
        #get categories of item
        categories = sqlitedb.getItemCategories(item_id)
        
        #figure out if the auction is closed or open
        auctionMessage = "Open"
        winning_bidder = None
        if not sqlitedb.hasAuctionStartedSQLOnly(item_id):
            auctionMessage = "Closed"
        if sqlitedb.hasAuctionEnded(item_id):
            auctionMessage = "Closed"
            if sqlitedb.getWinningBidder(item_id) is not None:
               winning_bidder =  sqlitedb.getWinningBidder(item_id)


        bids = sqlitedb.getBids(item_id)
        print bids[0]['UserID']
        if winning_bidder is not None:
            return render_template('single_item_view.html', results=result, categories=categories.Category, auctionMessage=auctionMessage, allBids = bids, winningBidder=winning_bidder)
        return render_template('single_item_view.html', results=result, categories=categories.Category, auctionMessage=auctionMessage, allBids = bids,)

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
