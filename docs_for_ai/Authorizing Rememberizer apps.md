# # Authorizing Rememberizer apps
Rememberizer's implementation supports the standard ~[authorization code grant type](https://tools.ietf.org/html/rfc6749#section-4.1)~. 
The web application flow to authorize users for your app is as follows:
*  Users are redirected to Rememberizer to authorize their account.  The user chooses mementos to use with your application.  Your application accesses the API with the user's access token.

⠀
Step 1. Request a user's Rememberizer identity

⠀Redirect the user to the Rememberizer authorization server to initiate the authentication and authorization process.
Copy
GET https://api.rememberizer.ai/api/v1/auth/oauth2/authorize/
Parameters:
| **name** | **description** |
|---|---|
| client_id | **Required**<br>The client ID for your application. You can find this value in the Developer Hub. |
| response_type | **Required**<br>Must be code for authorization code grants. |
| scope | A space-delimited list of scopes that identify the resources that your application could access on the user's behalf.  |
| redirect_uri | **Required**<br>The URL in your application where users will be sent after authorization. |
# Step 2. User choose and config their mementos
Users will choose which mementos to use with your app. 
# Step 3. Users are redirected back to your site by Rememberizer
After users select their mementos, Rememberizer redirects back to your site with a temporary code  parameter as well as the state you provided in the previous step in a state parameter. The temporary code will expire after a short time. If the states don't match, a third party created the request, and you should abort the process.
# Step 4. Exchange authorization code for refresh and access tokens
Copy
POST https://api.rememberizer.ai/api/v1/auth/oauth2/token/
This endpoint takes the following input parameters.
| **name** | **description** |
|---|---|
| client_id | **Required**<br>The client ID for your application. You can find this value in the Developer Hub. |
| client_secret | **Required**<br>The client secret you received from Rememberizer for your application. |
| code | The authorization code you recieved in step 3. |
| redirect_uri | **Required**<br>The URL in your application where users are sent after authorization. Must match with the redirect_uri in step 1. |
# Step 5. Use the access token to access the API
The access token allows you to make requests to the API on a user's behalf.
Copy
Authorization: Bearer OAUTH-TOKEN
GET https://api.rememberizer.ai/api/me
For example, in curl you can set the Authorization header like this:
Copy
curl -H "Authorization: Bearer OAUTH-TOKEN" https://api.rememberizer.ai/api/me
# References
Github: ~[https://github.com/skydeckai/rememberizer-integration-samples](https://github.com/skydeckai/rememberizer-integration-samples)~