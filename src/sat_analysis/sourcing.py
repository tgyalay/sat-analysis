'''
This module contains the logic for sourcing data from the web.
The main module will provide filtering criteria and the Sourcing class
will return time seires data for each of the satellites.
'''
import requests
import logging
from pprint import pformat
from datetime import datetime
from datetime import timezone
from .types import TleData, from_dict
from typing import Dict

import pyorbital.orbital

class SatDataFetcher:
    '''
    Handles sourcing of data from the N2YO API 
    and returns the json response as a dictionary
    '''
    def __init__(self, api_key, transaction_limit = 1000, base_url = 'https://api.n2yo.com/rest/v1/satellite/'):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')
        self.logger.info('Sourcing object created')
        self.transaction_limit = transaction_limit

    def _fetch_tle_data(self, satellite_id) -> dict:
        url = f'tle/{satellite_id}'
        return self.returner(url)
    
    def returner(self, path):
        '''
        Sends a request to the API and handles responses
        '''
        if self.api_key is None:
            raise ValueError('API Key is not set!')
        
        #only one type and we use
        url = self.base_url + path
        response = requests.get(url = url, params = {'apiKey': self.api_key})

        if response.status_code != 200:
            raise ValueError(
                f'Error in API call, status code: {response.status_code}'
                )
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
                if returned_dict['info']['transactionscount'] > (self.transaction_limit * .8):
                    self.logger.warning(f'Transaction count is approaching the limit: {self.transaction_limit}')
        return None


class SatPositionFetcher:
    '''
    Custodian of the TLE data and the satellite IDs
    Generates Position data for each satellite using the TLE data
    '''
    def __init__(self, api_key):
        self.data_fetcher = SatDataFetcher(api_key)
        self.satid_collection = set()
        self.satid_to_tle = {int : TleData}
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')

    def get_positions_over_time(self, time_values : list[datetime]):
        '''
        Returns a dictionary of dictionaries of positiosn over time for each satellite
        '''
        positions = {}
        for sat_id in self.satid_collection:
            tle_data = self.satid_to_tle[sat_id]
            positions[sat_id] = tle_data.get_positions_over_time(time_values)
        return positions
    
    #Single element updates
    def update_single_sat(self, sat_id : int):
        response = self.data_fetcher._fetch_tle_data(sat_id)
        self.satid_to_tle[sat_id] = from_dict(TleData, response)
        return

    def add_sat_id(self, sat_id):
        self.satid_collection.add(sat_id)
        try:
            self.update_single_sat(sat_id)
        except Exception as e:
            self.logger.error(
                f'Error adding satellite ID {sat_id}:\n{e.with_traceback()}'
                )
            #remove the satellite ID from the dictionary due to outdated data
            self.satid_to_tle.pop(sat_id) if sat_id in self.satid_to_tle else None

            return
        self.logger.info(f'Satellite ID {sat_id} added with TLE data and orbital information')

    #range updates
    def add_sat_id_range(self, sat_ids : list):
        for sat_id in sat_ids:
            self.add_sat_id(sat_id)

    def update_all_sats(self):
        failed_ids = []
        for sat_id in self.satid_collection:
            try:
                self.update_single_sat(sat_id)
            except Exception as e:
                self.logger.error(
                    f'Error updating satellite ID {sat_id}:\n{e.with_traceback()}'
                    )
                failed_ids.append(sat_id)
                
        logger_string = "All satellite IDs attempted update."
        if len(failed_ids) > 0:
            logger_string += f' Failed IDs:\n{pformat(failed_ids)}'
        else:
            logger_string += ' All IDs updated successfully.'
        self.logger.info(logger_string)

    def remove_sat_id(self, sat_id):
        if sat_id in self.satid_collection:
            self.satid_collection.remove(sat_id) 
        if sat_id in self.satid_to_tle:
            self.satid_to_tle.pop(sat_id) 