import pytest
from unittest.mock import Mock, patch, MagicMock
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@patch('app.requests.post')
def test_auth_rememberizer_callback(mock_post, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'access_token': 'mock_access_token', 'refresh_token': 'mock_refresh_token'}
    mock_post.return_value = mock_response
    response = client.get('/auth/rememberizer/callback?code=mock_auth_code')
    assert response.status_code == 302

    with client.session_transaction() as session:
        assert session['rememberizer_access_token'] == 'mock_access_token'
        assert session['rememberizer_refresh_token'] == 'mock_refresh_token'

@patch('app.requests.get')
def test_dashboard(mock_get, client):
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {'name': 'mock_data', 'email': 'mock_data'}
    mock_get.return_value = mock_response

    with client.session_transaction() as sess:
        sess['rememberizer_access_token'] = 'mock_access_token'
    response = client.get('/dashboard')

    assert response.status_code == 200
    assert b'mock_data' in response.data

@patch('app.OpenAI')
@patch('app.requests.get')
def test_ask(mock_requests_get, mock_openai, client):
    mock_response_get = MagicMock()
    mock_response_get.status_code = 200
    mock_response_get.json.return_value = {'mock_search_results': 'mock_data'}
    mock_requests_get.return_value = mock_response_get

    mock_openai_instance = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_message = MagicMock()
    mock_message.content = 'mock_answer'
    mock_completion.choices[0].message = mock_message
    mock_openai_instance.chat.completions.create.return_value = mock_completion
    mock_openai.return_value = mock_openai_instance

    with client.session_transaction() as sess:
        sess['rememberizer_access_token'] = 'mock_access_token'
    response = client.post('/ask', data={'question': 'mock_question'})

    assert response.status_code == 200
    assert b'mock_question' in response.data
    assert b'mock_answer' in response.data
