import logging
import logging.config

import pyorbital.orbital

#configure the logger
logger_config_path = "./config/logging.ini"
logging.config.fileConfig(logger_config_path)
logger = logging.getLogger(__name__)

import pyorbital.geoloc
import pytest
from sat_analysis import sourcing
from sat_analysis import types
import os
import pyorbital
import datetime

@pytest.fixture
def sourcing_obj() -> sourcing.SatDataFetcher:
    api_key = os.environ.get('N2YO_KEY')
    return sourcing.SatDataFetcher(api_key)

@pytest.fixture
def satellite_id():
    return '25544'

@pytest.fixture
def tle_response():
    return {
        'info': {
            'satid': 25544,
            'satname': 'SPACE STATION',
            'transactionscount': 0
            },
        'tle': '1 25544U 98067A   25040.72932104  .00010771  00000-0  19674-3 0  9995\r\n 2 25544  51.6371 218.3265 0003560 293.5013 159.2721 15.49953368495399'
        }

@pytest.fixture
def tle_response_obj(tle_response):
    tle_response_obj = types.Tle_Response(
        info = types.Info(
            satid = tle_response['info']['satid'],
            satname = tle_response['info']['satname'],
            transactionscount = tle_response['info']['transactionscount']
        ),
        tle = tle_response['tle']
    )
    return tle_response_obj


def test_get_tle(sourcing_obj : sourcing.SatDataFetcher, satellite_id):
    response = sourcing_obj._fetch_tle_data(satellite_id=satellite_id)

def test_json_to_dataclass(tle_response):
    tle_response_obj = sourcing.from_dict(sourcing.Tle_Response, tle_response)
    
    assert tle_response_obj.info.satid == tle_response["info"]["satid"]
    assert tle_response_obj.info.satname == tle_response["info"]["satname"]
    assert tle_response_obj.info.transactionscount == tle_response["info"]["transactionscount"]
    assert tle_response_obj.tle == tle_response["tle"]

    return

def test_get_sat_location(tle_response_obj : sourcing.Tle_Response):
    position = sourcing.SatPositionFetcher.get_position(tle_response_obj)
    logger.info(f'Position: {position}')
    return