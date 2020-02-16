#!/usr/bin/env python3
# Copyright (c) 2019 FRC Team 1678: Citrus Circuits
"""Sends web requests to The Blue Alliance (TBA) APIv3

Caches data to prevent duplicate data retrieval from the TBA API.
API documentation: https://www.thebluealliance.com/apidocs/v3"""
# External imports
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
    cached = local_database_communicator.select_tba_cache(api_url)
    # Check if cache exists
    if cached != {}:
        cached = cached[api_url]
        request_headers['If-Modified-Since'] = cached['timestamp']
    print(f'Retrieving data from {full_url}')
    try:
        request = requests.get(full_url, headers=request_headers)
    except requests.exceptions.ConnectionError:
        utils.log_warning('Error: No internet connection.')
        return None
    # A 200 status code means the request was successful
    # 304 means that data was not modified since the last timestamp
    # specified in request_headers['If-Modified-Since']
    if request.status_code == 304:
        return cached['data']
    if request.status_code == 200:
        formatted_data = {'timestamp': request.headers['Last-Modified'],
                                    'data': request.json()}
        local_database_communicator.overwrite_tba_data(formatted_data, api_url)
        return request.json()
    raise Warning(f'Request failed with status code {request.status_code}')


with open(utils.create_file_path('data/api_keys/tba_key.txt')) as file:
    API_KEY = file.read().rstrip('\n')
