# Rememberizer

This repository provides a collection of resources and examples to assist developers in integrating their applications with Rememberizer, a powerful knowledge management platform. It covers the entire integration process, from authenticating users and authorizing access to Rememberizer APIs, to leveraging the APIs to enhance applications with personalized, dynamic content from the user's knowledge base.

## Repository Structure

```
rememberizer-integration-samples/
├── docs_for_ai/
│   ├── Authorizing Rememberizer apps.md
│   └── developer_guide.md
├── gpt/
│   ├── README.md
│   └── rememberizer_openapi.yml
├── notebooks/
│   ├── .env.sample
│   ├── callback_server.py
│   └── developer_guide.ipynb
├── talk-to-slack/
│   ├── .env.sample
│   ├── README
│   ├── app.py
│   ├── requirements.txt
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   ├── answer.html
│   │   ├── chatbox.html
│   │   ├── dashboard.html
│   │   ├── error.html
│   │   ├── index.html
│   │   └── slack_info.html
│   └── test_app.py
```

### `docs_for_ai/`

This folder contains documentation files that provide valuable information for AI models and developers working on Rememberizer integrations:

- `Authorizing Rememberizer apps.md`: A comprehensive guide explaining the authorization flow for Rememberizer applications, including steps for requesting user authorization, exchanging authorization codes for access tokens, and using the access tokens to interact with the Rememberizer APIs.
- `developer_guide.md`: A detailed developer guide that walks through the entire process of integrating with Rememberizer, from registering your application to implementing the OAuth2 flow for user authorization and utilizing the Rememberizer APIs to access user data.

### `gpt/`

The `gpt/` folder contains resources specifically tailored for developers creating GPT models integrated with Rememberizer:

- `README.md`: A guide explaining the purpose and contents of this folder for creating Rememberizer-integrated GPT models.
- `rememberizer_openapi.yml`: An OpenAPI schema file that should be incorporated into your GPT model's OpenAPI specification to enable seamless integration with the Rememberizer APIs.

### `notebooks/`

This folder provides a Jupyter Notebook and a Flask server to facilitate the integration process:

- `.env.sample`: A sample environment file for configuring your application's credentials.
- `callback_server.py`: A Python script implementing a simple Flask server designed to handle the OAuth2 callback for Rememberizer integrations. This server listens for the redirect URI after a user authorizes your application, capturing the authorization code sent by Rememberizer.
- `developer_guide.ipynb`: A comprehensive Jupyter Notebook that serves as a step-by-step guide for developers looking to integrate with Rememberizer. It includes executable code snippets and explanatory text, covering the entire integration process from user authorization to API utilization.

Here's the walkthrough video:

https://github.com/skydeckai/rememberizer/assets/20924562/614ef839-9104-4e6f-9555-2dbea68e2130



### `talk-to-slack/`

The `talk-to-slack/` folder contains an example web application that integrates a language model (LLM) with user knowledge by making queries to Rememberizer:

- `.env.sample`: A sample environment file for configuring your application's credentials.
- `README`: A README file providing an overview of the contents and purpose of this folder.
- `app.py`: The main Flask application file that handles user authentication, Rememberizer API interactions, and rendering the web interface.
- `requirements.txt`: A list of Python dependencies required to run the application.
- `static/styles.css`: CSS styles for the web application.
- `templates/`: A folder containing HTML templates for rendering different pages of the web application.
- `test_app.py`: Unit tests for the Flask application.

## Getting Started

To get started with integrating your application with Rememberizer, follow these steps:

1. **Register Your Application**: Create a Rememberizer account and [register your application](https://docs.rememberizer.ai/developer/registering-rememberizer-apps) to obtain the necessary credentials for the OAuth2 flow and API access.

2. **User Authorization**: Implement the OAuth2 flow to allow your users to authorize your application to access their Rememberizer data. Refer to the `docs_for_ai/Authorizing Rememberizer apps.md` and `notebooks/developer_guide.ipynb` for detailed instructions.

3. **Utilize Rememberizer's APIs**: With the access tokens obtained in the previous step, your application can now make requests to the Rememberizer APIs to query and search through the user's data. Examples of API usage can be found in `notebooks/developer_guide.ipynb` and `talk-to-slack/app.py`.

For further assistance or inquiries, please refer to the [Rememberizer Documentation](https://docs.rememberizer.ai) or contact the Rememberizer support team.
