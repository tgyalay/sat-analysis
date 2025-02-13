import pytest
import os
from datetime import datetime, timedelta, timezone

from sat_analysis import sourcing
from sat_analysis import types

logger_config_path = "./config/logging.ini"

@pytest.fixture(scope='module')
def api_key():
    api_key = os.environ.get('N2YO_KEY')
    if api_key is None:
        raise ValueError('API Key is not set!')
    return api_key


@pytest.fixture
def data_fetcher(api_key) -> sourcing.SatDataFetcher:
    return sourcing.SatDataFetcher(api_key = api_key)

@pytest.fixture
def satellite_id():
    return '25544'

@pytest.fixture
def position_fetcher(api_key):
    pos_fetcher= sourcing.SatPositionFetcher(api_key= api_key)
    return pos_fetcher


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
    tle_response_obj = types.TleData(
        info = types.Info(
            satid = tle_response['info']['satid'],
            satname = tle_response['info']['satname'],
            transactionscount = tle_response['info']['transactionscount']
        ),
        tle = tle_response['tle']
    )
    return tle_response_obj


@pytest.fixture
def datetime_enumerable():
    #generate 5 datetime objects, representing each hour over the next five horus
    current_time = datetime.now(tz = timezone.utc)
    return [current_time + timedelta(hours=i) for i in range(5)]