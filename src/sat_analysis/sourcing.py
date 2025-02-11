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
from .types import Tle_Response, from_dict
from typing import Dict

import pyorbital.orbital

class SatDataFetcher:
    '''
    Handles sourcing of data from the N2YO API 
    and returns it in a structured format
    '''
    def __init__(self, api_key, transaction_limit = 1000, base_url = 'https://api.n2yo.com/rest/v1/satellite/'):
        self.api_key = api_key
        self.base_url = base_url
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')
        self.logger.info('Sourcing object created')
        self.transaction_limit = transaction_limit
    
    def _generate_tle_data(self, satellite_id) -> 'Tle_Response':
        response = self._fetch_tle_data(satellite_id)
        return from_dict(Tle_Response, response)

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
    Uses the pyorbital library to get the position of a satellite
    and the SatDataFetcher to get the TLE data for pyorbital
    '''
    def __init__(self, api_key):
        self.data_fetcher = SatDataFetcher(api_key)
        self.satid_collection = set()
        self.satid_to_tle = {int : Tle_Response}
        self.satid_to_orbitals = {int : pyorbital.orbital.Orbital}
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')

    #Single element updates
    def update_single_sat(self, sat_id : int):
        self.satid_to_tle[sat_id] = self.data_fetcher._generate_tle_data(sat_id)
        self.satid_to_orbitals[sat_id] = pyorbital.orbital.Orbital(
            "None",
            line1=self.satid_to_tle[sat_id].line1,
            line2=self.satid_to_tle[sat_id].line2
        )

    def add_sat_id(self, sat_id):
        self.satid_collection.add(sat_id)
        try:
            self.update_single_sat(sat_id)
        except Exception as e:
            self.logger.error(
                f'Error adding satellite ID {sat_id}:\n{e.with_traceback()}'
                )
            #remove the satellite ID from the collection
            self.satid_collection.remove(sat_id)
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
            logger_string += f' Failed IDs: {failed_ids}'
        self.logger.info(logger_string)

    @staticmethod
    def get_position(Tle_Response : 'Tle_Response', time = datetime.now(timezone.utc)):
        orbiter = pyorbital.orbital.Orbital(
            "None",
            line1 = Tle_Response.line1,
            line2 = Tle_Response.line2
        )
        return orbiter.get_lonlatalt(time)


