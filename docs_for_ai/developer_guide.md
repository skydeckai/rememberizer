# Rememberizer Developer Guide

Thank you for your interest in developing applications with Rememberizer. This guide is designed to walk you through the process of developing an application that integrates with Rememberizer, enhancing it by consolidating your users' content sources into personalized, dynamic knowledge bases.

To begin, you'll need to set up a server to handle the authorization callback. This is a crucial step in the OAuth2 flow. To facilitate this, we provide a simple Flask application in `callback.py` within this repository to help you get started quickly and efficiently.

## Basic Steps to Connect Your Application to Rememberizer:

1. **Register Your Application**: First, create a Rememberizer account and [register your application with Rememberizer](https://docs.rememberizer.ai/developer/registering-rememberizer-apps). This is a necessary step to obtain the credentials needed for the OAuth2 flow and API access.
2. **User Authorization**: Implement the OAuth2 flow to allow your users to authorize your application to access their Rememberizer data. This step is crucial for obtaining the access tokens needed to interact with the Rememberizer APIs.
3. **Utilize Rememberizer's APIs**: With the access tokens, your application can now make requests to Rememberizer's APIs. These APIs allow you to query and search through the user's data, enabling the integration of dynamic, personalized content into your application.

This guide will primarily focus on steps 2 and 3. For step 1, please ensure to follow the detailed instructions provided in the [Rememberizer app registration documentation](https://docs.rememberizer.ai/developer/registering-rememberizer-apps).

If you currently lack a server setup for handling the authorization callback, you can quickly get started with our provided Flask app. Running the following command will start a server on `http://localhost:5000/callback`, which will serve as the receiver for the authorization code:


    python callback_server.py



```python
import os
import requests, json
from IPython.display import display, HTML
```

## Authenticate with Rememberizer

Rememberizer's integration process adheres to the standard [Authorization Code Grant Type](https://tools.ietf.org/html/rfc6749#section-4.1), a secure method recommended for authenticating and authorizing users.

### Initiating the Authorization Process

To initiate the OAuth2 authorization process, your application must first redirect the user to Rememberizer's authorization URL. This is where the user will authenticate and choose which data (referred to as "mementos") to permit your application to access. Constructing this authorization URL involves appending several important query parameters:

- `client_id`: Your application's unique client ID, obtainable from the Developer Hub after registering your application with Rememberizer.
- `response_type`: This parameter should be set to `code`, indicating that you are using the authorization code grant type.
- `scope`: A space-delimited list of permissions your application is requesting. Each scope specifies access to a different type of data or action on behalf of the user.
- `state`: A CSRF (Cross-Site Request Forgery) token or other random string used to maintain state between the request and callback, enhancing security against CSRF attacks.

#### Constructing the Authorization URL:

The base URL for authorization will look something like this (not an actual URL, replace with Rememberizer's authorization endpoint):

    https://api.rememberizer.ai/api/v1/auth/oauth2/authorize

To this base URL, add the required query parameters, forming a complete URL:
    https://api.rememberizer.ai/api/v1/auth/oauth2/authorize?client_id=YOUR_CLIENT_ID&response_type=code&scope=REQUESTED_SCOPES&state=RANDOM_STATE


Replace `YOUR_CLIENT_ID`, `REQUESTED_SCOPES`, and `RANDOM_STATE` with your actual `client_id`, the scopes you're requesting, and a securely generated random state value, respectively.

Redirecting the user to this URL will start the authorization process. After logging in and approving access to their data, Rememberizer will redirect the user back to your application with an authorization code, which you can then exchange for an access token.



```python
client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]

redirect_uri = 'http://localhost:5000/callback'
scope = 'offline_access'  # Set this to offline access to get a refresh token. Otherwise you can left it as blank
state= '12345'

auth_url = 'https://api.rememberizer.ai/api/v1/auth/oauth2/authorize?response_type=code&client_id={}&redirect_uri={}&scope={}&state={}'.format(client_id, redirect_uri, scope, state)

# You need to redirect user to auth_url in your app. For now, you need to click on the link display. This will take you to the browser where you can login with Rememberizer and select Memento for your app.
# After authorizing, you will be redirected back to your callback_uri. You can get your authorization code there. If you're running the provided Flask server, you will be redirected to http://localhost:5000?code=AUTHORIZATION_CODE.
# Copy the code and paste it in the input field in this notebook.

display(HTML('<a href="{}" target="_blank"><h2>Click here to authenticate with Rememberizer</h2></a>'.format(auth_url)))
auth_code = input("Enter the authorization code: ")
print("Successfully getting authorization code.")
```

## Exchange authorization code for access token

After getting the authorization code, you need to exchange it by calling the exchange token endpoint. You will need to supply the client secret in this step.


```python
token_url = 'https://api.rememberizer.ai/api/v1/auth/oauth2/token/'

# Make the request for the access token
data = {
    'grant_type': 'authorization_code',
    'code': auth_code,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}

response = requests.post(token_url, data=data)
tokens = response.json()

if 'error' not in tokens:
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    print("Successfully getting the access token.")
else:
    print("Error getting the access token:")
    print(tokens)
```

### (Optionaly) Use refresh token to refresh access token
Access token expires after a while. If you want to refresh it, you can call the exchange token with the parameters below.


```python
token_url = 'https://api.rememberizer.ai/api/v1/auth/oauth2/token/'

data = {
    'grant_type': 'refresh_token',
    'refresh_token': refresh_token,
    'redirect_uri': redirect_uri,
    'client_id': client_id,
    'client_secret': client_secret
}

response = requests.post(token_url, data=data)
tokens = response.json()

if 'error' not in tokens:
    access_token = tokens.get('access_token')
    refresh_token = tokens.get('refresh_token')
    print("Successfully getting the access token.")
else:
    print("Error getting the access token:")
    print(tokens)
```

## Use access token to call Rememberizer APIs

Congratulation! You have acquired the access token. You can now attach it to the request header and make request to Rememberizer APIs.


```python
def call_api(api_url):
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.get(api_url, headers=headers)
    return response.json()
```


```python
print(json.dumps(call_api('https://api.rememberizer.ai/api/v1/integrations'), indent=2))
```


```python
print(json.dumps(call_api('https://api.rememberizer.ai/api/v1/account'), indent=2))
```


```python
print(json.dumps(call_api('https://api.rememberizer.ai/api/v1/documents'), indent=2))
```


```python
print(json.dumps(call_api('https://api.rememberizer.ai/api/v1/documents/search?q=kitty'), indent=2))
```


```python

```
