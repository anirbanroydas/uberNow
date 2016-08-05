from tornado.httpclient import AsyncHTTPClient, HTTPError
from tornado import gen
import json
import msgpack

import uberNow.utils


LOGGER = uberNow.utils.LOGGER

# Almabases's api key
API_KEY = 'AIzaSyB6ky0s6kmaxH15hsxsNHKuZeI6n_OG2eA'


DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?'




# Distamce Matrix level 1 status msgs
status1 = dict()
status1['OK'] = 'indicates the response contains a valid result'
status1['INVALID_REQUEST'] = 'Google Maps Distance Matrix Api request was invalid'
status1['MAX_ELEMENTS_EXCEEDED'] = 'Google Maps Distance Matrix Api indicates that the product of origins and destinations exceeds the per-query limit.'
status1['OVER_QUERY_LIMIT'] = 'Google Maps Distance Matrix Api indicates the service has received too many requests from your application within the allowed time period'
status1['REQUEST_DENIED'] = 'Google Maps Distance Matrix Api indicates that the service denied use of the Distance Matrix service by your application'
status1['UNKNOWN_ERROR'] = 'Google Maps Distance Matrix Api indicates the request could not be processed due to a server error. The request may succeed if you try again'

# Distance Matrix level 2 status msgs
status2 = dict()
status2['OK'] = 'Google Maps Distance Matrix Api indicates the response contains a valid result'
status2['NOT_FOUND'] = 'Google Maps Distance Matrix Api indicates that the origin and/or destination of this pairing could not be geocoded'
status2['ZERO_RESULTS'] = 'Google Maps Distance Matrix Api indicates no route could be found between the origin and destination'





@gen.coroutine
def fetch_travel_time(obj, origin, destination, dep_time, traffic_model):

    http_client = AsyncHTTPClient()
    url = DISTANCE_MATRIX_URL + 'origins=' + str(origin[0]) + ',' + str(origin[1]) +\
        '&destinations=' + str(destination[0]) + ',' + str(destination[1]) +\
        '&mode=driving&units=metric&departure_time=' + str(dep_time) +\
        '&traffic_model=' + traffic_model +\
        '&key=' + API_KEY

    response = None
    r = []

    try:
        # validate_cert=False to avoid certificate verify failed error
        response = yield http_client.fetch(url, validate_cert=False)

    except HTTPError, e:
        if e.code == 404 or e.code == 503 or e.code == 504 or e.code == 502:
            LOGGER.info({'location': 'uberNow.apps.apicalls.maps_api.fetch_travel_time',
                         'msg': str(e.__class__.__name__),
                         'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                         'request_url': url
                         })

            r = [-1, str(e.__class__.__name__), str(e), url]

            raise gen.Return(r)

        elif e.code == 400 or e.code == 422:
            msg_dict = dict()
            msg_dict['status'] = 'error_request'
            msg_dict['msg'] = 'Bad source or destination'
            msg_dict['req_time'] = uberNow.utils.localtime()

            obj.send(msgpack.packb(msg_dict, use_bin_type=True))

            LOGGER.error({'location': 'uberNow.apps.apicalls.maps_api.fetch_travel_time',
                          'msg': str(e.__class__.__name__),
                          'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                          'request_url': url
                          })

            r = [-2, 0, 0]

            raise gen.Return(r)

        else:
            LOGGER.critical({'location': 'uberNow.apps.apicalls.maps_api.fetch_travel_time',
                             'msg': str(e.__class__.__name__),
                             'description': str(e) + ' for websocket obj = [%s]' % str(obj.id),
                             'request_url': url
                             })
            r = [-3, 0, 0]

            raise gen.Return(r)

    json_response = json.loads(response.body)
    json_response['url'] = url

    res_time = process_travel_time(obj, json_response)

    raise gen.Return(res_time)





def process_travel_time(obj, doc):
    status = doc['status']
    msg_dict = dict()

    if status == 'OK':
        status_2 = doc['rows'][0]['elements'][0]['status']
        if status_2 == 'OK':
            duration = doc['rows'][0]['elements'][0]['duration']['value']
            duration_in_traffic = None
            if 'duration_in_traffic' in doc['rows'][0]['elements'][0]:
                duration_in_traffic = doc['rows'][0]['elements'][0]['duration_in_traffic']['value']
            else:
                duration_in_traffic = duration

            durations = [1, duration, duration_in_traffic]

            msg_dict['status'] = 'api_request'
            msg_dict['req_time'] = uberNow.utils.localtime()
            msg_dict['typ'] = 'Google Maps'
            msg_dict['email'] = obj.doc['email']

            obj.livestream_client.publish(msgpack.packb(
                msg_dict, use_bin_type=True), routing_key='live.*', exchange='livestream', delivery_mode=2)

            return durations
        else:
            LOGGER.error({'location': 'uberNow.apps.apicalls.maps_api.process_travel_time',
                          'msg': status_2,
                          'description': status2[status_2] + ' for websocket obj = [%s]' % str(obj.id),
                          'request_url': doc['url']
                          }) 


            msg_dict['status'] = 'error_request'
            msg_dict['msg'] = 'Bad source or destination'
            msg_dict['req_time'] = uberNow.utils.localtime()

            obj.send(msgpack.packb(msg_dict, use_bin_type=True))

            return [0, 'OK', status_2]

    elif status == 'UNKNOWN_ERROR':
        LOGGER.info({'location': 'uberNow.apps.apicalls.maps_api.process_travel_time',
                     'msg': status,
                     'description': status1[status] + ' for websocket obj = [%s]' % str(obj.id),
                     'request_url': doc['url']
                     }) 

        return [0, status, 0, doc['url']]

    elif status == 'OVER_QUERY_LIMIT':
        LOGGER.critical({'location': 'uberNow.apps.apicalls.maps_api.process_travel_time',
                         'msg': 'OVER_QUERY_LIMIT',
                         'description': status1[status] + ' for websocket obj = [%s]' % str(obj.id),
                         'request_url': doc['url']
                         })

    else:
        LOGGER.error({'location': 'uberNow.apps.apicalls.maps_api.process_travel_time',
                      'msg': status,
                      'description': status1[status] + ' for websocket obj = [%s]' % str(obj.id),
                      'request_url': doc['url']
                      })


    return [0, status, 0]













