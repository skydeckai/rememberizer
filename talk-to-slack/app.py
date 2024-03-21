# app.py
from flask import Flask, render_template, request, redirect, session
import requests
import os
import secrets
from openai import OpenAI
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get('APP_SECRET_KEY', 'your-secret-key')

REMEMBERIZER_CLIENT_ID = os.environ.get('REMEMBERIZER_CLIENT_ID')
REMEMBERIZER_CLIENT_SECRET = os.environ.get('REMEMBERIZER_CLIENT_SECRET')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/auth/rememberizer')
def auth_rememberizer():
    logging.debug('Auth Rememberizer route accessed')
    # Generate a random state value
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    redirect_uri = request.url_root + 'auth/rememberizer/callback'

    # Redirect to Rememberizer's authorization URL
    auth_url = (f'https://api.rememberizer.ai/api/v1/auth/oauth2/authorize?client_id={REMEMBERIZER_CLIENT_ID}'
                f'&response_type=code'
                f'&redirect_uri={redirect_uri}'
                f'&scope=offline_access'
                f'&state={state}')
    return redirect(auth_url)


@app.route('/auth/rememberizer/callback')
def auth_rememberizer_callback():
    # Exchange authorization code for access token
    auth_code = request.args.get('code')
    token_url = 'https://api.rememberizer.ai/api/v1/auth/oauth2/token/'
    redirect_uri = request.url_root + 'auth/rememberizer/callback'

    # Heroku setup
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': f'{redirect_uri}',
        'client_id': REMEMBERIZER_CLIENT_ID,
        'client_secret': REMEMBERIZER_CLIENT_SECRET
    }
    try:
        response = requests.post(token_url, data=data)
        tokens = response.json()
        session['rememberizer_access_token'] = tokens.get('access_token')
        session['rememberizer_refresh_token'] = tokens.get('refresh_token')
        return redirect('/dashboard')
    except Exception as e:
        logging.error(f'Error during token exchange: {e}')
        return redirect(f'/error?message={e}')  # Redirect to an error page or handle the error appropriately

@app.route('/dashboard')
def dashboard():
    if 'rememberizer_access_token' not in session:
        return redirect('/auth/rememberizer')
    headers = {'Authorization': f'Bearer {session["rememberizer_access_token"]}'}
    response = requests.get('https://api.rememberizer.ai/api/v1/account', headers=headers)
    if response.status_code != 200:
        return redirect('/auth/rememberizer')
    account_info = response.json()

    return render_template('dashboard.html', account_info=account_info)

@app.route('/slack-info')
def slack_info():
    logging.debug('Slack-info route accessed')
    if 'rememberizer_access_token' not in session:
        logging.debug('Access token not in session')
        return redirect('/auth/rememberizer')
    headers = {'Authorization': f'Bearer {session["rememberizer_access_token"]}'}
    
    try:
        response = requests.get('https://api.rememberizer.ai/api/v1/integrations', headers=headers)
        if response.status_code != 200:
            return redirect('/auth/rememberizer')
        
        slack_info = response.json()
        slack_integration = None
        for integration in slack_info['data']:
            if integration['integration_type'] == 'slack':
                slack_integration = integration
                break
        
        slack_channels = []
        if slack_integration:
            documents_response = requests.get(f'https://api.rememberizer.ai/api/v1/documents/', headers=headers)
            if documents_response.status_code != 200:
                raise Exception(f'Failed to fetch documents: {documents_response.status_code}')
            documents = documents_response.json()
            if documents.get('error'):
                raise Exception(f'Error in documents response: {documents["error"]}')
            results = documents['results']
            for result in results:
                if result['integration_type'] == 'slack':
                    slack_channels.append(result)
        
        return render_template('slack_info.html', slack_integration=slack_integration, slack_channels=slack_channels)
    except Exception as e:
        logging.error(f'Error in slack-info route: {e}')
        return redirect(f'/error?message={e}')


@app.route('/ask', methods=['POST'])
def ask():
    if 'rememberizer_access_token' not in session:
        return redirect('/auth/rememberizer')
    
    question = request.form['question']
    headers = {'Authorization': f'Bearer {session["rememberizer_access_token"]}'}
    response = requests.get(f'https://api.rememberizer.ai/api/v1/documents/search?q={question}&n=3', headers=headers)
    if response.status_code != 200:
        return redirect('/auth/rememberizer')
    search_results = response.json()
    
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Instruct the model to format its response in Markdown
    prompt = f"Q: {question}\nContext: {search_results}\nFormat your answer in Markdown:\nA:"
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a friendly AI assistant."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        model="gpt-4",
        temperature=0.7
    )
    answer = completion.choices[0].message

    # Pass the Markdown-formatted answer to the template
    return render_template('answer.html', question=question, answer=answer.content)


@app.route('/error')
def error():
    error_message = request.args.get('message', 'An unknown error occurred.')
    return render_template('error.html', error_message=error_message)

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the home page or login page
    return redirect('/')


if __name__ == '__main__':

    # this only gets used when running in localhost mode
    app.run(debug=True, ssl_context=('.env/cert.pem', '.env/key.pem'))