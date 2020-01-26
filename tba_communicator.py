#!/usr/bin/python3.6
"""Sends web requests to The Blue Alliance (TBA) APIv3

Caches data to prevent duplicate data retrieval from the TBA API.
API documentation: https://www.thebluealliance.com/apidocs/v3"""
# External imports
import time
import requests
# Internal imports
import local_database_communicator
import utils

def tba_request(api_url):
    """Sends a single web request to the TBA API v3

    api_url is the suffix of the API request URL
    (the part after '/api/v3')"""
    full_url = f'https://www.thebluealliance.com/api/v3/{api_url}'
    request_headers = {'X-TBA-Auth-Key': API_KEY}
    if cache_exists(api_url) is True:
        cached = local_database_communicator.select_one_from_database(
            {'tba_event_key': utils.TBA_EVENT_KEY}, {'tba_cache': 1})[api_url]
    else:
        cached = None
    if cached is not None:
        request_headers['If-Modified-Since'] = cached['timestamp']
    print(f'Retrieving data from {full_url}')
    try:
        request = requests.get(full_url, request_headers)
    except requests.exceptions.ConnectionError:
        utils.log_warning('Error: No internet connection.')
        return None
    # A 200 status code means the request was successful
    # 304 means that data was not modified since the last timestamp
    # specified in request_headers['If-Modified-Since']
    if request.status_code == 304:
        return cached['data']
    if request.status_code == 200:
        formatted_data = {api_url: {'timestamp': time.time(),
                                    'data': request.json()}}
        local_database_communicator.overwrite_document(formatted_data, 'tba_cache')
        return request.json()
    raise Warning(f'Request failed with status code {request.status_code}')


def cache_exists(api_url):
    """Returns True if a cached request for api_url exists in the database"""
    caches = local_database_communicator.select_one_from_database({},
                                                                  {f'tba_cache.{api_url}.data': 1})
    # Filter out caches with not data
    caches = [cache for cache in caches if len(cache['tba_cache']) > 0]
    return len(caches) > 0

with open(utils.create_file_path('data/api_keys/tba_key.txt')) as file:
    API_KEY = file.read().rstrip('\n')
