

from mock import Mock
import pytest
from pytest_couchdbkit.utils import dbname_from_config

def config(**data):
    mock = Mock()
    mock.getini = data.get
    return mock


def test_dbname_from_config():
    conf = config(couchdbkit_suffix='fun')

    name = dbname_from_config(conf, '%s')
    assert name == 'fun'

def test_skip_on_missing_suffix():
    conf = config()
    with pytest.raises(pytest.xfail.Exception):
        dbname_from_config(conf, '%s')
