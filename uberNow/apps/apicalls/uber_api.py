from tornado.httpclient import AsyncHTTPClient, HTTPError
# from tornado.ioloop import IOLoop
from tornado import gen
import json
import msgpack

import uberNow.utils


LOGGER = uberNow.utils.LOGGER

# Uber API endpoint
PRODUCT_URL = 'https://api.uber.com/v1/products?'

ETA_URL = "https://api.uber.com/v1/estimates/time?"

# Almabases's Server Token
SERVER_TOKEN = 'BPehDhjfmMaomcn2ZbnWuyaqRzrZoTS1ezAMlZs1'


def build_url(end_point, parameters):
    url = end_point + "?"
    ii = 0
    for index in parameters.keys():
        if(ii == 0):
            url = url + index + "=" + parameters[index]
        else:
            url = url + "&" + index + "=" + parameters[index]
        ii += 1
    return url


@gen.coroutine
def fetch_products(obj, source):
    http_client = AsyncHTTPClient()

    url = PRODUCT_URL + 'latitude=' + str(source[0]) +\
        '&longitude=' + str(source[1]) +\
        '&server_token=' + SERVER_TOKEN

    response = None
    try:
        # validate_cert=False to avoid certificate verify failed error
        response = yield http_client.fetch(url, validate_cert=False)

    except Exception, e:
        LOGGER.critical({'location': 'uberNow.apps.apicalls.uber_api.fetch_products',
                         'msg': str(e.__class__.__name__),
                         'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                         'request_url': url
                         })

        raise gen.Return(-100)

    msg_dict = dict() 
    msg_dict['status'] = 'api_request'
    msg_dict['req_time'] = uberNow.utils.localtime()
    msg_dict['typ'] = 'Uber'
    msg_dict['email'] = obj.doc['email']

    obj.livestream_client.publish(msgpack.packb(
                msg_dict, use_bin_type=True), routing_key='live.*', exchange='livestream', delivery_mode=2)


    json_response = json.loads(response.body)
    products = json_response['products']

    if len(products) == 0:
        raise gen.Return(-1)

    else:
        for item in products:
            if item['display_name'] == 'uberGO':
                raise gen.Return(item['product_id'])

        raise gen.Return(-1)







@gen.coroutine
def fetch_eta(obj, source):
    http_client = AsyncHTTPClient()

    url = ETA_URL + 'start_latitude=' + str(source[0]) +\
        '&start_longitude=' + str(source[1]) +\
        '&server_token=' + SERVER_TOKEN

    response = None
    msg_dict = dict() 
    r = []

    try:
        # validate_cert=False to avoid certificate verify failed error
        response = yield http_client.fetch(url, validate_cert=False)

    except HTTPError, e:
        if e.code == 404 or e.code == 503 or e.code == 504 or e.code == 502: 
            LOGGER.info({'location': 'uberNow.apps.apicalls.maps_api.fetch_eta',
                         'msg': str(e.__class__.__name__),
                         'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                         'request_url': url
                         }) 

            r = [-1, str(e.__class__.__name__), str(e), url]

            raise gen.Return(r)


        elif e.code == 400 or e.code == 422: 
            msg_dict['status'] = 'error_request'
            msg_dict['error'] = 'Bad source or destination'
            msg_dict['req_time'] = uberNow.utils.localtime()
            
            obj.send(msgpack.packb(msg_dict, use_bin_type=True)) 

            LOGGER.error({'location': 'uberNow.apps.apicalls.maps_api.fetch_eta',
                          'msg': str(e.__class__.__name__),
                          'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                          'request_url': url
                          })
            
            r = [-2]

            raise gen.Return(r)

        else: 
            LOGGER.critical({'location': 'uberNow.apps.apicalls.uber_api.fetch_eta',
                             'msg': str(e.__class__.__name__),
                             'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                             'request_url': url
                             })

            r = [-3]

            raise gen.Return(r)

     
    msg_dict['status'] = 'api_request'
    msg_dict['req_time'] = uberNow.utils.localtime()
    msg_dict['typ'] = 'Uber'
    msg_dict['email'] = obj.doc['email']

    obj.livestream_client.publish(msgpack.packb(
                msg_dict, use_bin_type=True), routing_key='live.*', exchange='livestream', delivery_mode=2)

    json_response = json.loads(response.body)
    products = json_response['times']

    print 'products : \n'
    print products

    if len(products) == 0:
        r = [-4]

        raise gen.Return(r)

    else:
        for item in products:
            print 'item : \n'
            print item
            if item['display_name'] == 'uberGO':
                r = [1, item['estimate']]
                
                raise gen.Return(r)

        r = [-4]

        raise gen.Return(r)




# Test calls
# start_loc = (12999.9248619, 77999.6318783)
# end_loc = (12.9702942, 77.6087463)

# IOLoop.instance().run_sync(lambda: fetch_eta(start_loc))

