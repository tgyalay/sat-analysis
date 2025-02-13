import logging
import logging.config
from pprint import pformat

from sat_analysis import sourcing
from sat_analysis import types
from fixtures import (
    api_key,
    data_fetcher,
    satellite_id, 
    tle_response,
    tle_response_obj,
    position_fetcher,
    logger_config_path
)

#configure the logger
logging.config.fileConfig(logger_config_path)
logger = logging.getLogger(__name__)

def test_get_tle(data_fetcher : sourcing.SatDataFetcher, satellite_id):
    response = data_fetcher._fetch_tle_data(satellite_id=satellite_id)

def test_json_to_dataclass(tle_response):
    tle_response_obj = sourcing.from_dict(sourcing.TleData, tle_response)
    
    assert tle_response_obj.info.satid == tle_response["info"]["satid"]
    assert tle_response_obj.info.satname == tle_response["info"]["satname"]
    assert tle_response_obj.info.transactionscount == tle_response["info"]["transactionscount"]
    assert tle_response_obj.tle == tle_response["tle"]

    return

def test_get_sat_location(tle_response_obj : sourcing.TleData):
    position = tle_response_obj.get_position()
    logger.info(f'Position: {position}')
    return
