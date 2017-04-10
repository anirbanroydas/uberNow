import pytest
from uberNow.server import main as uberNow_app


@pytest.fixture(scope='session')
def app():
    return uberNow_app
    