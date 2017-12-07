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
        '/timetable','timetable'
        # TODO: add additional URLs here
        # first parameter => URL, second parameter => class name
        )
class search:
    def GET(self):
        return render_template('search.html')





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
        t = sqlitedb.transaction()
        # try:
        #     sqlitedb.query('[FIRST QUERY STATEMENT]')
        #     sqlitedb.query('[SECOND QUERY STATEMENT]')
        # except Exception as e:
        #     t.rollback()
        #     print str(e)
        # else:
        #     t.commit()
        try:
            current_time = sqlitedb.getTime()
            update_message = 'Bid set on item:%s at $%s' \
                         ' at %s' % ((itemID), (price), (current_time))
            sqlitedb.insertBid(itemID, userID, price, current_time)
        except Exception as e:
            t.rollback()
            print str(e)
            update_message = 'Invalid bid, please enter a new valid bid'
        else:
            t.commit()
        # Here, we assign `update_message' to `message', which means
        # we'll refer to it in our template as `message'
        return render_template('add_bid.html', message=update_message)


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

###########################################################################################
##########################DO NOT CHANGE ANYTHING BELOW THIS LINE!##########################
###########################################################################################

if __name__ == '__main__':
    web.internalerror = web.debugerror
    app = web.application(urls, globals())
    app.add_processor(web.loadhook(sqlitedb.enforceForeignKey))
    app.run()
