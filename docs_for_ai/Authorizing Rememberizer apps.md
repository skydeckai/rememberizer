# Authorizing Rememberizer apps

Rememberizer's implementation supports the standard [authorization code grant type](https://tools.ietf.org/html/rfc6749#section-4.1).&#x20;

The web application flow to authorize users for your app is as follows:

1. Users are redirected to Rememberizer to authorize their account.
2. The user chooses mementos to use with your application.
3. Your application accesses the API with the user's access token.

### Step 1. Request a user's Rememberizer identity

Redirect the user to the Rememberizer authorization server to initiate the authentication and authorization process.

```
GET https://api.rememberizer.ai/api/v1/auth/oauth2/authorize/
```

Parameters:

<table><thead><tr><th width="165">name</th><th>description</th></tr></thead><tbody><tr><td>client_id</td><td><strong>Required</strong><br>The client ID for your application. You can find this value in the Developer Hub.</td></tr><tr><td>response_type</td><td><strong>Required</strong><br>Must be <code>code</code> for authorization code grants.</td></tr><tr><td>scope</td><td>A space-delimited list of scopes that identify the resources that your application could access on the user's behalf. </td></tr><tr><td>redirect_uri</td><td><strong>Required</strong><br>The URL in your application where users will be sent after authorization.</td></tr></tbody></table>

### Step 2. User choose and config their mementos

Users will choose which mementos to use with your app.&#x20;

### Step 3. Users are redirected back to your site by Rememberizer

After users select their mementos, Rememberizer redirects back to your site with a temporary `code`  parameter as well as the state you provided in the previous step in a `state` parameter. The temporary code will expire after a short time. If the states don't match, a third party created the request, and you should abort the process.

### Step 4. Exchange authorization code for refresh and access tokens

```
POST https://api.rememberizer.ai/api/v1/auth/oauth2/token/
```

This endpoint takes the following input parameters.

<table><thead><tr><th width="165">name</th><th>description</th></tr></thead><tbody><tr><td>client_id</td><td><strong>Required</strong><br>The client ID for your application. You can find this value in the Developer Hub.</td></tr><tr><td>client_secret</td><td><strong>Required</strong><br>The client secret you received from Rememberizer for your application.</td></tr><tr><td>code</td><td>The authorization code you recieved in step 3.</td></tr><tr><td>redirect_uri</td><td><strong>Required</strong><br>The URL in your application where users are sent after authorization. Must match with the redirect_uri in step 1.</td></tr></tbody></table>

### Step 5. Use the access token to access the API

The access token allows you to make requests to the API on a user's behalf.

```
Authorization: Bearer OAUTH-TOKEN
GET https://api.rememberizer.ai/api/me
```

For example, in curl you can set the Authorization header like this:

```shell
curl -H "Authorization: Bearer OAUTH-TOKEN" https://api.rememberizer.ai/api/me
```
