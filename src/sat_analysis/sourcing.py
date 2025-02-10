'''
This module contains the logic for sourcing data from the web.
The main module will provide filtering criteria and the Sourcing class
will return time seires data for each of the satellites.
'''
import requests
import logging
from pprint import pformat

class Sourcing:
    def __init__(self, api_key, transaction_limit = 1000):
        self.api_key = api_key
        self.base_url = 'https://api.n2yo.com/rest/v1/satellite/'
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')
        self.logger.info('Sourcing object created')
        self.transaction_limit = transaction_limit

    def _get_tle(self, satellite_id):
        url = f'tle/{satellite_id}'
        return self.returner(url)
    
    def returner(self, path):
        if self.api_key is None:
            raise ValueError('API Key is not set!')
        
        #only one type and we use
        url = self.base_url + path
        response = requests.get(url = url, params = {'apiKey': self.api_key})

        if response.status_code != 200:
            raise ValueError(f'Error in API call, status code: {response.status_code}')
        response_json = response.json()
        self.logger.debug(f'Response:\n{pformat(response_json)}')
        if 'error' in response_json:
            raise ValueError(f'Error in API call: {response_json["error"]}')
        
        self.check_transaction_count(response_json)
        return response_json
        
    def check_transaction_count(self, returned_dict : dict):
        if 'info' in returned_dict:
            if 'transactionscount' in returned_dict['info']:
                #check if transaction count is approaching the limit
                if returned_dict['info']['transactionscount'] > self.transaction_limit * .8:
                    self.logger.warning(f'Transaction count is approaching the limit: {self.transaction_limit}')
        return None


    

