# README

This repo includes:

- `developer_guide.ipynb`: This Jupyter Notebook serves as a comprehensive guide for developers looking to integrate with Rememberizer. It includes step-by-step instructions on registering your application, implementing OAuth2 for user authorization, and utilizing Rememberizer's APIs to access user data. The notebook combines explanatory text with executable code snippets, offering a hands-on approach to learning the integration process.

- `callback_server.py`: This Python script implements a simple Flask server designed to handle the OAuth2 callback for Rememberizer integrations. It listens for the redirect URI after a user authorizes your application, capturing the authorization code sent by Rememberizer. This code is then used to request access tokens for API interactions. The script is an essential component for developers without an existing server setup, facilitating quick and easy OAuth2 flow testing and implementation.

- `rememberizer_openapi.yml`: OpenAPI schema to put in the GPT.

- `talk-to-slack`: An example web application that integrates an LLM with user knowledge by making queries to Rememberizer.

- `docs_for_ai`: To maximize the efficiency and innovation in application development, include the documents from the docs_for_ai folder into the LLM's context. This comprehensive integration provides the LLM with a wide range of information, enabling it to deliver more accurate and relevant outputs. Simply add the entire contents of the docs_for_ai folder to enrich the LLM context.

Here is a walkthrough video:

https://github.com/skydeckai/rememberizer-integration-samples/assets/95598734/27c9053c-34f9-44dd-8027-bba08cbc3c80


## Resources

[Rememberizer: A First-Time Developer Guide](https://try.rememberizer.ai/blog/rememberizer-a-first-time-developer-guide)

[Creating a Rememberizer GPT](https://docs.rememberizer.ai/developer/creating-a-rememberizer-gpt)

[Authorizing Rememberizer apps](https://docs.rememberizer.ai/developer/authorizing-rememberizer-apps)
