# test_cli.py
import pytest
from biobricks.cli import register_on_biobricks

# Using requests_mock to mock API responses
@pytest.fixture
def mock_request(requests_mock):
    mock_url = 'https://biobricks.ai/api/register'
    mock_response = {
        'auth_numbers': '12345',
        'auth_url': 'https://biobricks.ai/auth'
    }
    requests_mock.post(mock_url, json=mock_response, status_code=200)
    return requests_mock  # This return isn't necessary but can be useful if you want to add more specifics in the fixture.

def test_register_on_biobricks(mock_request):  # This should be the fixture name.
    result = register_on_biobricks('test@example.com')
    
    assert result['message'] == "Authentication needed."
    assert result['auth_numbers'] == '12345'
    assert result['auth_url'] == 'https://biobricks.ai/auth'
