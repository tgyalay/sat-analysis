import pytest
import logging
import logging.config
from pprint import pformat

from sat_analysis.sourcing import SatDataFetcher, SatPositionFetcher
from fixtures import (
    api_key,
    position_fetcher,
    satellite_id,
    datetime_enumerable,
    logger_config_path
)

#configure the logger
logging.config.fileConfig(logger_config_path)
logger = logging.getLogger(__name__)

def test_get_positions_over_time(position_fetcher : SatPositionFetcher, datetime_enumerable, satellite_id):
    position_fetcher.add_sat_id(satellite_id)
    positions = position_fetcher.get_positions_over_time(datetime_enumerable)
    
    assert len(positions) > 0
    logger.info(f'Positions:\n{pformat(positions)}')

    return

def test_update_tle(position_fetcher : SatPositionFetcher, satellite_id):
    position_fetcher.add_sat_id(satellite_id)
    position_fetcher.update_all_sats()
    return