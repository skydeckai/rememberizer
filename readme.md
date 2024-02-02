- `developer_guide.ipynb`: This Jupyter Notebook serves as a comprehensive guide for developers looking to integrate with Rememberizer. It includes step-by-step instructions on registering your application, implementing OAuth2 for user authorization, and utilizing Rememberizer's APIs to access and manipulate user data. The notebook combines explanatory text with executable code snippets, offering a hands-on approach to learning the integration process.

- `callback_server.py`: This Python script implements a simple Flask server designed to handle the OAuth2 callback for Rememberizer integrations. It listens for the redirect URI after a user authorizes your application, capturing the authorization code sent by Rememberizer. This code is then used to request access tokens for API interactions. The script is an essential component for developers without an existing server setup, facilitating quick and easy OAuth2 flow testing and implementation.