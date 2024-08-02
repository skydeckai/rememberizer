import unittest
from unittest.mock import MagicMock, patch

from provider import (
    FUNCTION_MAPPING,
    RememberizerSourceProvider,
    generate_extra_knowledge_message,
)


class TestRememberizerSourceProvider(unittest.TestCase):

    def setUp(self):
        self.access_token = "test_access_token"
        self.provider = RememberizerSourceProvider(self.access_token)
        self.mock_response = MagicMock()
        self.mock_response.json.return_value = {"data": "test"}
        self.mock_response.status_code = 200

    def test_initialization(self):
        self.assertEqual(self.provider.access_token, self.access_token)

    @patch("provider.requests.get")
    def test_call_api_get(self, mock_get):
        mock_get.return_value = self.mock_response
        response = self.provider.call_api("http://test.url", method="get")
        self.assertEqual(response, self.mock_response)
        mock_get.assert_called_once_with(
            "http://test.url",
            headers={"Authorization": f"Bearer {self.access_token}"},
            params={},
            verify=False,
        )

    @patch("provider.requests.post")
    def test_call_api_post(self, mock_post):
        mock_post.return_value = self.mock_response
        response = self.provider.call_api(
            "http://test.url", method="post", params={"key": "value"}
        )
        self.assertEqual(response, self.mock_response)
        mock_post.assert_called_once_with(
            "http://test.url",
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"key": "value"},
            verify=False,
        )

    def test_format_response_success(self):
        response, success = self.provider.format_response(self.mock_response)
        self.assertTrue(success)
        self.assertEqual(response, {"data": "test"})

    def test_format_response_failure(self):
        self.mock_response.status_code = 400
        response, success = self.provider.format_response(self.mock_response)
        self.assertFalse(success)
        self.assertEqual(response, {"data": "test"})

    def test_responses_to_text(self):
        user_message = "Test message"
        response = {"data": "test"}
        expected_text = "Knowledge source: Rememberizer\n\tUser: Test message\n\tResponse: {'data': 'test'}\n\n"
        self.assertEqual(
            self.provider.responses_to_text(user_message, response), expected_text
        )

    @patch.object(RememberizerSourceProvider, "call_api")
    def test_search(self, mock_call_api):
        mock_call_api.return_value = self.mock_response
        response, success = self.provider.search({"q": "test query"})
        self.assertTrue(success)
        self.assertEqual(response, {"data": "test"})
        mock_call_api.assert_called_once_with(
            FUNCTION_MAPPING["search"][2], params={"q": "test query"}
        )

    @patch.object(RememberizerSourceProvider, "call_api")
    def test_get_account(self, mock_call_api):
        mock_call_api.return_value = self.mock_response
        response, success = self.provider.get_account({})
        self.assertTrue(success)
        self.assertEqual(response, {"data": "test"})
        mock_call_api.assert_called_once_with(FUNCTION_MAPPING["account"][2], params={})

    @patch.object(RememberizerSourceProvider, "call_api")
    def test_get_discussion_content(self, mock_call_api):
        mock_call_api.return_value = self.mock_response
        response, success = self.provider.get_discussion_content({"discussion_id": 123})
        self.assertTrue(success)
        self.assertEqual(response, {"data": "test"})
        mock_call_api.assert_called_once_with(
            FUNCTION_MAPPING["get_discussion_content"][2].format(123),
            params={"integration_type": "slack"},
        )

    @patch.object(RememberizerSourceProvider, "call_api")
    def test_list_channels(self, mock_call_api):
        mock_call_api.return_value = self.mock_response
        response, success = self.provider.list_channels({})
        self.assertTrue(success)
        self.assertEqual(response, {"data": "test"})
        mock_call_api.assert_called_once_with(
            FUNCTION_MAPPING["list_channels"][2], params={}
        )

    @patch.object(RememberizerSourceProvider, "search")
    def test_call_function(self, mock_search):
        mock_search.return_value = ({"data": "test"}, True)
        response = self.provider.call_function("search", {"q": "test query"})
        self.assertEqual(response, {"data": "test"})
        mock_search.assert_called_once_with({"q": "test query"})

    @patch("provider.RememberizerSourceProvider.call_function")
    @patch("provider.RememberizerSourceProvider.responses_to_text")
    @patch("provider.generate_extra_knowledge_message")
    @patch("provider.json.loads")
    def test_handle(
        self,
        mock_json_loads,
        mock_generate_extra_knowledge_message,
        mock_responses_to_text,
        mock_call_function,
    ):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.tool_calls = [MagicMock()]
        mock_response.choices[0].message.tool_calls[0].function.name = "search"
        mock_response.choices[0].message.tool_calls[
            0
        ].function.arguments = '{"q": "test query"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_json_loads.return_value = {"q": "test query"}
        mock_call_function.return_value = {"data": "test"}
        mock_responses_to_text.return_value = "extra content"
        mock_generate_extra_knowledge_message.return_value = "raw content"

        result = self.provider.handle("Test message", mock_client)
        self.assertEqual(result, "raw content")
        mock_client.chat.completions.create.assert_called_once()
        mock_call_function.assert_called_once_with("search", {"q": "test query"})
        mock_responses_to_text.assert_called_once_with("Test message", {"data": "test"})
        mock_generate_extra_knowledge_message.assert_called_once_with(
            extra_knowledge="extra content", request_type="GET"
        )

    def test_generate_extra_knowledge_message_get(self):
        extra_knowledge = "Extra knowledge"
        request_type = "GET"
        expected_message = (
            "Below are some extra knowledge. Use it if necessary:\nExtra knowledge\n\n"
            "### Instructions\n- Use the provided knowledge to answer the user's query.\n"
            "- Ensure the response is accurate and relevant to the query.\n"
        )
        self.assertEqual(
            generate_extra_knowledge_message(extra_knowledge, request_type),
            expected_message,
        )

    def test_generate_extra_knowledge_message_post(self):
        extra_knowledge = "Extra knowledge"
        request_type = "POST"
        expected_message = (
            "The action has been completed. Below is the extra knowledge obtained from the action:\nExtra knowledge\n\n"
            "### Instructions\n- Use the provided knowledge to generate a comprehensive response.\n"
            "- Ensure the information is relevant and accurately reflects the result of the action.\n"
        )
        self.assertEqual(
            generate_extra_knowledge_message(extra_knowledge, request_type),
            expected_message,
        )


if __name__ == "__main__":
    unittest.main()
