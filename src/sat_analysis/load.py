import numpy as np
import logging

class SatelliteData():

    '''
    This class abstracts the logic for storing and retrieving the
    time series data for the satellites.
    '''

    def __init__(self):
        # the incoming data is a dictionary of dictionaries of the form 
        # {satellite_id: {datetime: {logitude, latitude, altitude}}}
        self.sat_data = np.ndarray(shape = (0, 0, 0), dtype = object)
        self.logger = logging.getLogger(__name__+f'.{self.__class__.__name__}')
        self.logger.info('SatelliteData object created')

    def add_satellite(self, sat_id : int, data : dict):
        '''
        Adds a satellite to the data structure.
        data is of form {datetime: {logitude, latitude, altitude}}
        '''
        pass