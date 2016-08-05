from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import json

from .celery import app
import uberNow.utils


LOGGER = uberNow.utils.LOGGER

# Almabases's api key
API_KEY = 'AIzaSyB6ky0s6kmaxH15hsxsNHKuZeI6n_OG2eA'


DISTANCE_MATRIX_URL = 'https://maps.googleapis.com/maps/api/distancematrix/json?'

'origins=12.0453705,77.58068179&destinations=12.9693669,77.6410758&mode=driving&units=metric&departure_time=1468847700&traffic_model=pessimistic&key=AIzaSyB6ky0s6kmaxH15hsxsNHKuZeI6n_OG2eA'





def build_url(location, category):
    return (DISTANCE_MATRIX_URL +
            'origins=' + str(origin[0]) + ',' + str(origin[1]) +
            '&destinations=' + str(destination[0]) + ',' + str(destination[1]) +
            '&mode=driving&units=metric&departure_time=' + str(dep_time) +
            '&traffic_model=' + traffic_model +
            '&key=' + API_KEY
            )


@gen.coroutine
def fetch_places(location, category):
    global ICON_URL_MAP
    """
    This functions takes 2 params - location a tuple of the form (latitude, longitude) and 
    a string denoting the category of product desired
    Returns a formatted JSON response
    """
    http_client = AsyncHTTPClient()
    request = build_search_url(location, category)
    print request
    # validate_cert=False to avoid certificate verify failed error
    response = yield http_client.fetch(request, validate_cert=False)
    json_response = json.loads(response.body)
    print json_response
    json_response = replace_icons(json_response, ICON_URL_MAP[category])

    print json_response
    gen.Return(json_response)



@app.task
@gen.coroutine
def fetch_travel_time(origin, destination, dep_time, traffic_model):
    http_client = AsyncHTTPClient()
    url = DISTANCE_MATRIX_URL + 'origins=' + str(origin[0]) + ',' + str(origin[1]) +\
        '&destinations=' + str(destination[0]) + ',' + str(destination[1]) +\
        '&mode=driving&units=metric&departure_time=' + str(dep_time) +\
        '&traffic_model=' + traffic_model +\
        '&key=' + API_KEY

    # validate_cert=False to avoid certificate verify failed error
    response = yield http_client.fetch(url, validate_cert=False)
    json_response = json.loads(response.body)
    new_dep_time = process_travel_time_response(json_response)
    






