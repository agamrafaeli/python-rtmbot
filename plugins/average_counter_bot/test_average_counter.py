from itertools import combinations
from random import randint
from unittest import TestCase

from mock import MagicMock

import average_counter_bot


class AverageCounterTestCase(TestCase):
    def setUp(self):
        self.known_user_name = "MOCK USER NAME"
        self.known_user_slack_id = "MOCK SLACK ID"

        self.mock_slack_client = MagicMock()

    def test_average_counter_is_zero(self):
        average_counter_bot.ALL_USERS_COUNTER = 0
        return_average = average_counter_bot.average()
        self.assertEqual(return_average, average_counter_bot.NO_NUMBERS_WRITTEN_YET)

    def test_average_valid(self):
        average_counter_bot.ALL_USERS_COUNTER = randint(1, 20)
        average_counter_bot.ALL_USERS_SUM = randint(20, 1000)
        return_average = average_counter_bot.average()
        expected_average = str(average_counter_bot.ALL_USERS_SUM / average_counter_bot.ALL_USERS_COUNTER)
        self.assertEqual(return_average, expected_average)

    def test_average_user_known_user(self):
        average_counter_bot.AVERAGE_PER_USER_DICT = {}
        random_total = randint(20, 1000)
        random_counter = randint(1, 20)
        average_counter_bot.AVERAGE_PER_USER_DICT[self.known_user_slack_id] = {
            'total': random_total,
            'counter': random_counter
        }
        return_average = average_counter_bot.average_user(username_to_search=self.known_user_slack_id,
                                                          slack_client=self.mock_slack_client)
        self.assertEqual(return_average, str(random_total / random_counter))

    def test_average_known_user_by_human_readable_username_exists(self):
        average_counter_bot.AVERAGE_PER_USER_DICT = {}
        random_total = randint(20, 1000)
        random_counter = randint(1, 20)
        average_counter_bot.AVERAGE_PER_USER_DICT[self.known_user_slack_id] = {
            'total': random_total,
            'counter': random_counter
        }

        self.mock_slack_client.api_call = MagicMock(return_value={
            "ok": True,
            "members": [{
                "name": self.known_user_name,
                "id": self.known_user_slack_id
            }]
        })

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)
        self.assertEqual(return_average, str(random_total / random_counter))

    def test_average_known_user_by_human_readable_username_does_not_exist_locally(self):
        average_counter_bot.AVERAGE_PER_USER_DICT = {}

        self.mock_slack_client.api_call = MagicMock(return_value={
            "ok": True,
            "members": [{
                "name": self.known_user_name,
                "id": self.known_user_slack_id
            }]
        })

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)

        self.assertEqual(return_average, average_counter_bot.NO_SUCH_USER_FOUND)

    def test_average_known_user_by_human_readable_username_two_users_found_on_server(self):
        self.mock_slack_client.api_call = MagicMock(return_value={
            "ok": True,
            "members": [
                {
                    "name": self.known_user_name,
                    "id": self.known_user_slack_id
                },
                {
                    "name": self.known_user_name,
                    "id": "OTHER ID"
                }]
        })

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)

        self.assertEqual(return_average, average_counter_bot.MORE_THAN_ONE_USER_BE_MORE_SPECIFIC)

    def test_average_known_user_by_human_readable_username_not_found_on_server(self):
        self.mock_slack_client.api_call = MagicMock(return_value={
            "ok": True,
            "members": [{
                    "name": "UNKNOWN USER NAME",
                    "id": "UNKNOWN ID"
                }]
        })

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)

        self.assertEqual(return_average, average_counter_bot.NO_SUCH_USER_FOUND)

    def test_average_known_user_by_human_readable_username_got_ok_field_false(self):
        # Initialized for possible good answer
        average_counter_bot.AVERAGE_PER_USER_DICT = {}
        random_total = randint(20, 1000)
        random_counter = randint(1, 20)
        average_counter_bot.AVERAGE_PER_USER_DICT[self.known_user_slack_id] = {
            'total': random_total,
            'counter': random_counter
        }

        self.mock_slack_client.api_call = MagicMock(return_value={
            "ok": False,
            "members": [{
                "name": self.known_user_name,
                "id": self.known_user_slack_id
            }]
        })

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)

        self.assertEqual(return_average, average_counter_bot.NO_SUCH_USER_FOUND)

    def test_average_known_user_by_human_readable_exception_on_going_slack(self):
        self.mock_slack_client.api_call = MagicMock(side_effect=Exception())

        return_average = average_counter_bot.average_user(username_to_search=self.known_user_name,
                                                          slack_client=self.mock_slack_client)

        self.assertEqual(return_average, average_counter_bot.NO_SUCH_USER_FOUND)

    def test_process_message_field_validation(self):
        message = {}
        average_counter_bot.outputs = []
        return_code = average_counter_bot.process_message(message)
        self.assertEqual(return_code, False)
        self.assertEqual(average_counter_bot.outputs, [])

        message = {'user':''}
        average_counter_bot.outputs = []
        return_code = average_counter_bot.process_message(message)
        self.assertEqual(return_code, False)
        self.assertEqual(average_counter_bot.outputs, [])

        message = {'text': ''}
        average_counter_bot.outputs = []
        return_code = average_counter_bot.process_message(message)
        self.assertEqual(return_code, False)
        self.assertEqual(average_counter_bot.outputs, [])

        message = {'channel': ''}
        average_counter_bot.outputs = []
        return_code = average_counter_bot.process_message(message)
        self.assertEqual(return_code, False)
        self.assertEqual(average_counter_bot.outputs, [])

        for sublist_of_fields in combinations(['user', 'text', 'channel'], 2):
            average_counter_bot.outputs = []
            message = {}
            for field in sublist_of_fields:
                message[field] = ''
            return_code = average_counter_bot.process_message(message)
            self.assertEqual(return_code, False)
            self.assertEqual(average_counter_bot.outputs, [])

    def test_process_message_non_text_message(self):
        average_counter_bot.outputs = []
        message = {
            'user': '',
            'channel': '',
            'text': 'NOT A NUMBER'
        }

        return_code = average_counter_bot.process_message(message)
        self.assertEqual(return_code, False)
        self.assertEqual(average_counter_bot.outputs, [])

    def test_process_message_valid_message_new_user(self):
        mock_user_id = 'MOCK_USER_ID'
        mock_channel_name = 'MOCK_CHANNEL_ID'
        mock_sum = randint(1, 100)
        mock_message = {
            'user': mock_user_id,
            'channel': mock_channel_name,
            'text': str(mock_sum)
        }

        average_counter_bot.ALL_USERS_COUNTER = 0
        average_counter_bot.ALL_USERS_SUM = 0
        average_counter_bot.CURRENT_PERIOD_COUNTER = 0
        average_counter_bot.CURRENT_PERIOD_SUM = 0
        average_counter_bot.AVERAGE_PER_USER_DICT = {}
        average_counter_bot.LAST_CHANNEL_TO_SEND_MESSAGE = ''
        average_counter_bot.outputs = []
        
        return_code = average_counter_bot.process_message(mock_message)
        self.assertEqual(return_code, True)

        self.assertEqual(average_counter_bot.ALL_USERS_COUNTER, 1)
        self.assertEqual(average_counter_bot.ALL_USERS_SUM, mock_sum)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_COUNTER, 1)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_SUM, mock_sum)
        self.assertTrue(mock_user_id in average_counter_bot.AVERAGE_PER_USER_DICT)
        expected_user_average_dict = {
            'total': mock_sum,
            'counter': 1
        }
        self.assertDictEqual(average_counter_bot.AVERAGE_PER_USER_DICT[mock_user_id], expected_user_average_dict)
        self.assertEqual(average_counter_bot.LAST_CHANNEL_TO_SEND_MESSAGE, mock_channel_name)
        self.assertTrue(len(average_counter_bot.outputs) > 0)

    def test_process_message_valid_message_existing_user(self):
        mock_user_id = 'MOCK_USER_ID'
        mock_channel_name = 'MOCK_CHANNEL_ID'
        mock_sum = randint(1, 100)
        mock_message = {
            'user': mock_user_id,
            'channel': mock_channel_name,
            'text': str(mock_sum)
        }

        mock_all_users_counter = randint(1, 20)
        average_counter_bot.ALL_USERS_COUNTER = mock_all_users_counter
        mock_all_users_sum = randint(20, 1000)
        average_counter_bot.ALL_USERS_SUM = mock_all_users_sum
        mock_current_period_counter = randint(1, 20)
        average_counter_bot.CURRENT_PERIOD_COUNTER = mock_current_period_counter
        mock_current_period_sum = randint(20, 1000)
        average_counter_bot.CURRENT_PERIOD_SUM = mock_current_period_sum
        average_counter_bot.AVERAGE_PER_USER_DICT = {}
        mock_specific_user_total = randint(5, 10)
        mock_specific_user_counter = randint(1, 5)
        average_counter_bot.AVERAGE_PER_USER_DICT[mock_user_id] = {
            'total': mock_specific_user_total,
            'counter': mock_specific_user_counter
        }
        average_counter_bot.LAST_CHANNEL_TO_SEND_MESSAGE = ''

        return_code = average_counter_bot.process_message(mock_message)
        self.assertEqual(return_code, True)

        self.assertEqual(average_counter_bot.ALL_USERS_COUNTER, mock_all_users_counter + 1)
        self.assertEqual(average_counter_bot.ALL_USERS_SUM, mock_all_users_sum + mock_sum)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_COUNTER, mock_current_period_counter + 1)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_SUM, mock_current_period_sum + mock_sum)
        self.assertTrue(mock_user_id in average_counter_bot.AVERAGE_PER_USER_DICT)
        expected_user_average_dict = {
            'total': mock_specific_user_total + mock_sum,
            'counter': mock_specific_user_counter + 1
        }
        self.assertDictEqual(average_counter_bot.AVERAGE_PER_USER_DICT[mock_user_id], expected_user_average_dict)
        self.assertEqual(average_counter_bot.LAST_CHANNEL_TO_SEND_MESSAGE, mock_channel_name)
        self.assertTrue(len(average_counter_bot.outputs) > 0)

    def test_all_people_average_last_minute_no_messages(self):
        average_counter_bot.outputs = []
        average_counter_bot.CURRENT_PERIOD_COUNTER = 0

        average_counter_bot.all_people_average_last_minute()

        self.assertEqual(average_counter_bot.outputs, [])
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_SUM, 0.0)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_COUNTER, 0)

    def test_all_people_average_last_minute_has(self):
        average_counter_bot.outputs = []
        mock_counter = randint(1, 20)
        average_counter_bot.CURRENT_PERIOD_COUNTER = mock_counter
        mock_sum = randint(20, 1000)
        average_counter_bot.CURRENT_PERIOD_SUM = mock_sum

        average_counter_bot.all_people_average_last_minute()

        self.assertTrue(len(average_counter_bot.outputs) > 0)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_SUM, 0.0)
        self.assertEqual(average_counter_bot.CURRENT_PERIOD_COUNTER, 0)

