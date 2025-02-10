import logging
import logging.config

#configure the logger
logger_config_path = "./config/logging.ini"
logging.config.fileConfig(logger_config_path)

import pytest
from sat_analysis.sourcing import Sourcing
import os

@pytest.fixture
def sourcing_obj() -> Sourcing:
    api_key = os.environ.get('N2YO_KEY')
    return Sourcing(api_key)

@pytest.fixture
def satellite_id():
    return '25544'

def test_get_tle(sourcing_obj : Sourcing, satellite_id):
    response = sourcing_obj._get_tle(satellite_id=satellite_id)
