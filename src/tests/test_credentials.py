import sys
import pytest
from unittest import mock
import getpass

# Import the module
from youtube_history.credentials import get_password

@pytest.fixture(autouse=True)
def mock_sys_platform(request):
    """Mock sys.platform to 'win32' for Windows tests"""
    if request.node.get_closest_marker("windows"):
        with mock.patch.object(sys, 'platform', "win32"):
            yield
    else:
        yield

@pytest.fixture(autouse=True)
def mock_keyring(request):
    """Mock keyring module for Windows tests"""
    if request.node.get_closest_marker("windows"):
        with mock.patch("credentials.keyring") as mock_keyring:
            yield mock_keyring
    else:
        yield None

def test_getpwd_linux(monkeypatch):
    """Test getpwd function on Linux"""
    item = "example"
    username = "testuser"
    expected_password = "testpass"
    
    # Mock the getpass.getpass function
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: expected_password)
    
    # Call the function
    password = get_password(item, username)
    
    # Assert the password
    assert password == expected_password

def test_gotify_credentials():
    assert get_password("gotify", "HomeServer") != ''
    