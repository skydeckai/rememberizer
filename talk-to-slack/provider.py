import json
import logging
import os

import requests
from constants import (
    REMEMBERIZER_ACCOUNT_ENDPOINT,
    REMEMBERIZER_DISCUSSION_CONTENT_ENDPOINT,
    REMEMBERIZER_SEARCH_ENDPOINT,
    REMEMBERIZER_SLACK_INTEGRATIONS_ENDPOINT,
)

logger = logging.getLogger(__name__)

REMEMBERIZER_CLIENT_ID = os.environ.get("REMEMBERIZER_CLIENT_ID")
REMEMBERIZER_CLIENT_SECRET = os.environ.get("REMEMBERIZER_CLIENT_SECRET")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GPT_MODEL = os.environ.get("GPT_FUNCTION_CALLING_MODEL", "gpt-4o")

FUNCTION_CALLING_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Initiate a search with a query of up to 400 words to get highly relevant responses from stored knowledge. For Q&A, transform your question into an ideal answer format to find similar existing answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Up to 400 words sentence for which you wish to find semantically similar chunks of knowledge.",
                    },
                    "n": {
                        "type": "integer",
                        "description": "Number of semantically similar chunks of text to return. Use 'n=3' for up to 5, and 'n=10' for more information. If you do not receive enough information, consider trying again with a larger 'n' value.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_discussion_content",
            "description": "Get the content of the Slack channel with the specified primary key. The response contains 2 fields, discussion_content, and thread_contents. The former contains the main messages of the chat, whereas the latter is the threads of the discussion.",
            "parameters": {
                "type": "object",
                "properties": {
                    "discussion_id": {
                        "type": "integer",
                        "description": "The primary key of the document",
                    },
                    "from": {
                        "type": "string",
                        "description": "The starting time when we want to retrieve the content of the discussion in ISO 8601 format at GMT+0. If not specified, the default time is now.",
                    },
                    "to": {
                        "type": "string",
                        "description": "The ending time when we want to retrieve the content of the discussion in ISO 8601 format at GMT+0. If not specified, it is 7 days before the 'from' parameter.",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "account",
            "description": "Get the Rememberizer account information",
        },
    },
    {
        "type": "function",
        "function": {"name": "list_channels", "description": "List all Slack channels"},
    },
]

FUNCTION_MAPPING = {
    "search": ("search", "GET", REMEMBERIZER_SEARCH_ENDPOINT),
    "account": ("get_account", "GET", REMEMBERIZER_ACCOUNT_ENDPOINT),
    "list_channels": (
        "list_channels",
        "GET",
        REMEMBERIZER_SLACK_INTEGRATIONS_ENDPOINT,
    ),
    "get_discussion_content": (
        "get_discussion_content",
        "GET",
        REMEMBERIZER_DISCUSSION_CONTENT_ENDPOINT,
    ),
}


def generate_extra_knowledge_message(extra_knowledge: str, request_type: str) -> str:
    if request_type == "GET":
        return (
            f"Below are some extra knowledge. Use it if necessary:\n{extra_knowledge}\n\n"
            f"### Instructions\n- Use the provided knowledge to answer the user's query.\n"
            f"- Ensure the response is accurate and relevant to the query.\n"
        )
    elif request_type == "POST":
        return (
            f"The action has been completed. Below is the extra knowledge obtained from the action:\n{extra_knowledge}\n\n"
            f"### Instructions\n- Use the provided knowledge to generate a comprehensive response.\n"
            f"- Ensure the information is relevant and accurately reflects the result of the action.\n"
        )


class RememberizerSourceProvider:
    def __init__(self, access_token):
        self.access_token = access_token

    def call_api(self, url, params={}, method="get", retried=False):
        headers = {"Authorization": f"Bearer {self.access_token}"}
        if method == "post":
            response = requests.post(url, headers=headers, data=params, verify=False)
        elif method == "get":
            response = requests.get(url, headers=headers, params=params, verify=False)
        else:
            raise Exception(
                f"[Rememberizer Source Error] Method not supported: {method}"
            )
        return response

    def format_response(self, response):
        """
        Format the response from the API
        Returns: data (dict), success (bool)
        """
        return response.json(), response.status_code == 200

    def responses_to_text(self, user_message, response):
        text = "Knowledge source: Rememberizer\n"
        text += f"\tUser: {user_message}\n"
        text += f"\tResponse: {response}\n\n"

        return text

    def search(self, arguments):
        response = self.call_api(f"{REMEMBERIZER_SEARCH_ENDPOINT}", params=arguments)
        return self.format_response(response)

    def get_account(self, arguments):
        response = self.call_api(f"{REMEMBERIZER_ACCOUNT_ENDPOINT}", params=arguments)
        return self.format_response(response)

    def get_discussion_content(self, arguments):
        discussion_id = arguments.pop("discussion_id")
        arguments["integration_type"] = "slack"
        response = self.call_api(
            REMEMBERIZER_DISCUSSION_CONTENT_ENDPOINT.format(discussion_id),
            params=arguments,
        )
        return self.format_response(response)

    def list_channels(self, arguments):
        response = self.call_api(
            f"{REMEMBERIZER_SLACK_INTEGRATIONS_ENDPOINT}", params=arguments
        )
        return self.format_response(response)

    def call_function(self, function_name, arguments):
        response, success = getattr(self, function_name)(arguments)

        if not success:
            logger.error(f"Error calling function {function_name}")

        return response

    def handle(
        self,
        message,
        client,
        gpt_model=GPT_MODEL,
        function_calling_tools=FUNCTION_CALLING_TOOLS,
        function_mapping=FUNCTION_MAPPING,
    ):
        try:
            tool_choice_prompt = [
                {"role": "system", "content": "You are a friendly AI assistant."},
                {"role": "user", "content": message},
            ]

            chat_response = client.chat.completions.create(
                messages=tool_choice_prompt,
                model=gpt_model,
                tools=function_calling_tools,
            )

            if not chat_response.choices[0].message.tool_calls:
                return "No context provided"

            tools_response = chat_response.choices[0].message
            tool_calls = tools_response.tool_calls
            function_name = tool_calls[0].function.name
            arguments = json.loads(tool_calls[0].function.arguments)

            if function_name not in function_mapping:
                logger.error(
                    f"Function {function_name} not found in the list of functions"
                )
                return {}

            logger.debug(f"Calling {function_name} with arguments {arguments}")
            provider_function_name, request_type, _ = function_mapping[function_name]

            response = self.call_function(provider_function_name, arguments)
            extra_content = self.responses_to_text(message, response)
            raw_content = generate_extra_knowledge_message(
                extra_knowledge=extra_content,
                request_type=request_type,
            )

            return raw_content

        except Exception as ex:
            logger.error(
                f"Something went wrong while connecting with Rememberizer. {str(ex)}",
                exc_info=True,
            )
            return {}
