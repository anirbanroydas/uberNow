"""
This is the main view module which manages main tornado connections. This module
provides request handlers for managing simple HTTP requests as well as Websocket requests.

Although the websocket requests are actually sockJs requests which follows the sockjs protcol, thus it
provide interface to sockjs connection handlers behind the scene.
"""



from __future__ import absolute_import

import tornado.web
import tornado.escape
from tornado import gen
# import logging
import msgpack
import random
import time
from sockjs.tornado import SockJSConnection
from validate_email import validate_email


from ..rabbitmq.pubsub import RabbitMqClient
import uberNow.utils
from ..apicalls import uber_api as uber
from ..apicalls import maps_api as maps
from ..apicalls import email_api as email
from ..apicalls import mongodb_api as mongo

# LOGGER = logging.getLogger(__name__)
LOGGER = uberNow.utils.LOGGER

# Number of starting times enough to predict a possible starting time
ST_MAX = 3

# Maximum Number of maps api calls to be made for getting a predictive soltion per user request
MAPS_TRIES_MAX = 10

# Time in seconds left to reach destination at destination_time error margin
TIME_LEFT_ERROR_MARGIN = 60

# Time in seconds left to make critical calls bypassing all other predictions
CRITICAL_CLOSE_CALLS = 600

# Maximum Deviation in seconds in Traffic time, presently 1 hour/ 60 min
MAX_DEVIATION = 3600

# Maximum Deviation of current time to departure time in seconds
MAX_DEP_TIME_DEVIATION = 30

# Fuzzy latency between current time and actual exceution of api at google maps api in seconds
FUZZY_LATENCY = 60

# Maximum number of retries to do in case of Google Maps in situations
# like unknown error, service temporarily unavailable
MAX_MAPS_API_RETRIES = 10



# Returns a backoff time for retrying a function
def backoff(retries):
    return int(random.uniform(2, 4) ** retries)




# Handles the general HTTP connections
class IndexHandler(tornado.web.RequestHandler):
    """This handler is a basic regular HTTP handler to serve the chatroom page.

    """

    def get(self):
        """
        This method is called when a client does a simple GET request,
        all other HTTP requests like POST, PUT, DELETE, etc are ignored.

        :return: Returns the rendered main requested page, in this case its the chat page, index.html

        """

        LOGGER.info('[IndexHandler] HTTP connection opened')

        self.render('index.html')

        LOGGER.info('[IndexHandler] index.html served')










# Handler for Websocket Connections or Sockjs Connections
class UbernowRequestHandler(SockJSConnection):
    """ Websocket Handler implementing the sockjs Connection Class which will
    handle the websocket/sockjs connections.
    """


    def on_open(self, conn_info):
        """
        This method is called when a websocket/sockjs connection is opened for the first time.

        :param      self:  The object
        :param      conn_info:  The connection related information

        :return:    It returns the websocket object

        """

        LOGGER.info('[UbernowRequestHandler] Websocket connecition opened: %s ' % self)


        self.db = self.application.db
        self.redis = self.application.redis
        self.with_celery = self.application.with_celery
        self.model = self.application.model
        self.scheduler = self.application.scheduler

        self.id = uberNow.utils.genid(32)

        self.livestream_client = RabbitMqClient(queue='livestream_queue-' + str(self.id),
                                                exchange='livestream',
                                                exchange_type='topic',
                                                exchange_durability=True,
                                                queue_binding_key='live.*',
                                                queue_durability=True,
                                                queue_exclusivity=True,
                                                queue_auto_delete=True,
                                                person=self.id
                                                )
        self.livestream_client.websocket = self
        self.livestream_client.start()

        self.maps_req_retries = 0
        self.uber_req_retries = 0
        self.count = 1
        self.doc = None

        # ST - Starting Time dictionary with starting times as keys and values as
        # time to reach destination before required time
        self.ST = dict()

        # ST Tries Dictionary - contaning all the starting times that has been
        # tries for the given request
        self.st_tries_dict = dict()



        # adding new websocket connection to global websocketParcticipants set
        # websocketParticipants.add(self)



    @gen.coroutine
    def on_message(self, message):
        """
        This method is called when a message is received via the websocket/sockjs connection
        created initially.

        :param      self:     The object
        :param      message:  The message received via the connection.
        :type       message: json string

        """

        # LOGGER.info('[ChatWebsocketHandler] message received on Websocket: %s ' % self)

        proceed = False

        self.doc = msgpack.unpackb(message, encoding='utf-8')

        verify = self.sanitize(self.doc)

        if not verify['is_good']:
            self.doc['status'] = 'bad_input'
            self.doc['req_time'] = uberNow.utils.localtime()
            self.doc['bad_inputs'] = verify['bad_inputs']

            self.send(msgpack.packb(self.doc, use_bin_type=True))
            return

        self.utc = uberNow.utils.local2UTC(self.doc['destination_time'])
        # Insert document to MongoDB for first time
        if self.count == 1:


            self.count = 2

            self.doc['_id'] = self.id
            # insert record to MONGODB
            h = yield self.insert2mongo(new_id=self.id)

            if h > -1:
                # insert record to Redis
                self.id = h
                del self.doc['_id']

                r = self.insert2redis()

                if r is True:

                    self.doc['status'] = 'new_request'
                    self.doc['req_time'] = uberNow.utils.localtime()

                    proceed = True

                else:
                    pass

            else:
                pass



        else:
            # if client sends updated request info due to previous anomalies handle it

            # update record in MONGODB
            h = yield self.update2mongo(new_id=self.id)

            if h.modified_keys == 1:

                # update record in Redis
                r = self.insert2redis()

                if r is True:

                    self.doc['status'] = 'updated_request'
                    self.doc['req_time'] = uberNow.utils.localtime()

                    proceed = True

                else:
                    pass

            else:
                pass


        if proceed:
            self.livestream_client.publish(msgpack.packb(
                self.doc, use_bin_type=True), routing_key='live.*', exchange='livestream', delivery_mode=2)

            if self.with_celery:
                pass

            else:
                p = yield self.process_maps_api(uberNow.utils.epoch())
                if p == 1:
                    pass

                elif p == 0:
                    pass

                else:
                    pass


        else:
            self.doc['status'] = 'server_error'
            self.doc['req_time'] = uberNow.utils.localtime()

            self.send(msgpack.packb(self.doc, use_bin_type=True))










    def on_close(self):
        """
        This method is called when a websocket/sockjs connection is closed.

        :param      self:  The object

        :return:     Doesn't return anything, except a confirmation of closed connection back to web app.

        """

        LOGGER.info('[UbernowRequestHandler] Websocket conneciton close event %s ' % self)

        # Close the connection
        self.livestream_client.stop()

        LOGGER.info('[UbernowRequestHandler] Websocket connection closed')






    def sanitize(self, inputs):
        is_good = True
        bad_inputs = []

        if not self.is_good_coordinate(inputs['source']):
            is_good = False
            bad_inputs.append('source')
        else:
            self.doc['source'] = inputs['source'].split(',')

        if not self.is_good_coordinate(inputs['destination']):
            is_good = False
            bad_inputs.append('destination')
        else:
            self.doc['destination'] = inputs['destination'].split(',')


        t = self.doc['destination_time']
        self.doc['destination_time'] = uberNow.utils.formLocalTime(
            t['hour'], t['mins'], t['meridian'])

        if not validate_email(inputs['email']):
            is_good = False
            bad_inputs.append('email')

        verify = {'is_good': is_good,
                  'bad_inputs': bad_inputs
                  }

        return verify





    def is_good_coordinate(self, coordinate_string):
        s = coordinate_string.strip()
        c1 = s.count(',')

        if c1 == 1:
            s_l = s.split(',')
            if s_l[0].count('.') == 1 and s_l[1].count('.') == 1:
                s_l_l = s_l[0].split('.')
                s_l_r = s_l[1].split('.')

                if s_l_l[0].isdigit() and s_l_l[1].isdigit() and s_l_r[0].isdigit() and s_l_r[1].isdigig():
                    return True
                else:
                    return False
            else:
                return False

        else:
            return False





    @gen.coroutine
    @mongo.handle_failover
    def insert2mongo(self, new_id=None):
        self.id = new_id
        self.doc['_id'] = self.id

        res = yield self.db.requests_collection.insert(self.doc)

        raise gen.Return(res)




    @gen.coroutine
    @mongo.handle_failover
    def update2mongo(self, new_id=None):

        res = yield self.db.requests_collection.replace_one({'_id': self.id}, self.doc)

        raise gen.Return(res)



    def insert2redis(self):
        try:
            res = self.redis.setex(self.id, msgpack.packb(
                self.doc, use_bin_type=True), uberNow.utils.expires(self.doc['time']))
            return res
        except Exception, e:
            LOGGER.error({'location': 'uberNow.apps.main.views.insert2redis',
                          'msg': str(e.__class__.__name__),
                          'description': str(e) + ' for websocket obj = [%s]' % str(self.id)
                          })
            return False





    @gen.coroutine
    def process_maps_api(self, dep_time):
        temp_dep_time = dep_time
        while self.maps_tries < MAPS_TRIES_MAX:
            if str(dep_time) != 'now' and dep_time < time.time() and (time.time() - dep_time) > MAX_DEP_TIME_DEVIATION:
                raise gen.Return(0)
            elif str(dep_time) != 'now' and (dep_time < time.time() or (dep_time - time.time()) < FUZZY_LATENCY):
                dep_time = 'now'
                temp_dep_time = time.time()

            durations = yield maps.fetch_travel_time(self, self.doc['source'], self.doc['destination'], dep_time, self.model)

            r1, r2, r3 = durations[0], durations[1], durations[2]

            dep_time = temp_dep_time

            if r1 == -3: 
                raise gen.Return(-1)


            elif r1 == -1 or (r1 == 0 and r2 == 'UNKNOWN_ERROR'):
                self.maps_req_retries = self.maps_req_retries + 1

                if self.maps_req_retries > MAX_MAPS_API_RETRIES:
                    LOGGER.critical({'location': 'uberNow.apps.apicalls.maps_api.fetch_travel_time',
                                     'msg': r2,
                                     'description': r3 + ' for websocket obj = [%s]' % str(self.id),
                                     'request_url': durations[3]
                                     })

                    raise gen.Return(-2)

                t = backoff(self.maps_req_retries)

                yield gen.sleep(t)

                res = yield self.process_maps_api(dep_time)

                raise gen.Return(res)

            elif r1 == -2 or (r1 == 0 and r2 == 'OK'):
                raise gen.Return(-3)

            elif r1 == 1:
                self.maps_tries = self.maps_tries + 1
                time_left = uberNow.utils.timeLeft(self.utc)
                diff_abs = abs(time_left - r3)
                diff = time_left - r3
                if diff_abs <= TIME_LEFT_ERROR_MARGIN:
                    raise gen.Return(-4)

                elif diff > 0 and diff > TIME_LEFT_ERROR_MARGIN and diff <= CRITICAL_CLOSE_CALLS:
                    raise gen.Return(-5)

                else:
                    reaching_time = uberNow.utils.newTimeAdd(dep_time, r3)
                    reaching_margin = self.utc - reaching_time

                    if len(self.ST) == 0:
                        self.ST[dep_time] = reaching_margin
                        new_dep_time = uberNow.utils.newTimeSub(self.utc, (r3 + MAX_DEVIATION))

                        if new_dep_time < time.time():
                            new_dep_time = uberNow.utils.newTimeSub(self.utc, r3)

                    elif reaching_margin >= 0 and len(self.ST) < ST_MAX:
                        max_margin = reaching_margin
                        max_key = dep_time

                        for key in self.ST.keys():
                            if max_margin < self.ST[key]:
                                max_margin = self.ST[key]
                                max_key = key

                        new_dep_time = uberNow.utils.newTimeSub(self.utc, r3)

                        self.ST[dep_time] = reaching_margin


                    elif reaching_margin >= 0 and reaching_margin < max_margin:
                        del self.ST[max_key]
                        self.ST[dep_time] = reaching_margin
                        max_margin = reaching_margin
                        max_key = dep_time

                        for key in self.ST.keys():
                            if max_margin < self.ST[key]:
                                max_margin = self.ST[key]
                                max_key = key


                        new_dep_time = uberNow.utils.newTimeSub(self.utc, r3)

                    else:
                        new_dep_time = uberNow.utils.newTimeSub(self.utc, r3)

                    if new_dep_time in self.st_tries_dict:
                        raise gen.Return(1)

                    else:
                        self.st_tries_dict[new_dep_time] = 1

                        res = yield self.process_maps_api(new_dep_time)

                        raise gen.Return(res)




            else:
                raise gen.Return(-6)


        raise gen.Return(1)








