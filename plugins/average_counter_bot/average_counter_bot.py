from __future__ import unicode_literals
# don't convert to ascii in py2.7 when creating string to return

from threading import Thread
from bottle import route, run
from client import slack_client as sc

crontable = []
outputs = []

# Configuration variables
PERIOD_DURATION = 60

# Internal management variables
CURRENT_PERIOD_SUM = 0.0
CURRENT_PERIOD_COUNTER = 0

ALL_USERS_SUM = 0.0
ALL_USERS_COUNTER = 0.0

LAST_CHANNEL_TO_SEND_MESSAGE = ''

AVERAGE_PER_USER_DICT = {}

# String Constants
MORE_THAN_ONE_USER_BE_MORE_SPECIFIC = "The username given returned multiple users. Please be more specific"
NO_SUCH_USER_FOUND = "No such user found"
NO_NUMBERS_WRITTEN_YET = "No numbers written yet"

crontable.append([PERIOD_DURATION, "all_people_average_last_minute"])


def process_message(message):
    global outputs

    global CURRENT_PERIOD_SUM
    global CURRENT_PERIOD_COUNTER

    global ALL_USERS_COUNTER
    global ALL_USERS_SUM

    global LAST_CHANNEL_TO_SEND_MESSAGE

    list_of_fields_to_check = ['user', 'text', 'channel']
    if not all(field in message.keys() for field in list_of_fields_to_check):
        return False

    LAST_CHANNEL_TO_SEND_MESSAGE = message['channel']

    try:
        this_number = int(message['text'])
    except Exception:
        return False

    ALL_USERS_COUNTER += 1
    ALL_USERS_SUM += this_number

    CURRENT_PERIOD_SUM += this_number
    CURRENT_PERIOD_COUNTER += 1

    if message['user'] not in AVERAGE_PER_USER_DICT:
        AVERAGE_PER_USER_DICT[message['user']] = {
            'total': 0.0,
            'counter': 0
        }

    AVERAGE_PER_USER_DICT[message['user']]['counter'] += 1
    AVERAGE_PER_USER_DICT[message['user']]['total'] += int(message['text'])
    user_average = AVERAGE_PER_USER_DICT[message['user']]['total'] / AVERAGE_PER_USER_DICT[message['user']]['counter']
    resp_dict = {
        'user': message['user'],
        'counter': str(AVERAGE_PER_USER_DICT[message['user']]['counter']),
        'total': str(AVERAGE_PER_USER_DICT[message['user']]['total']),
        'average': user_average
    }
    user_average_message = "The user %(user)s's average is %(average)s" % resp_dict
    outputs.append([LAST_CHANNEL_TO_SEND_MESSAGE, user_average_message])

    return True


def all_people_average_last_minute():
    global outputs

    global CURRENT_PERIOD_COUNTER
    global CURRENT_PERIOD_SUM
    global LAST_CHANNEL_TO_SEND_MESSAGE

    if CURRENT_PERIOD_COUNTER > 0:
        all_users_average = CURRENT_PERIOD_SUM / CURRENT_PERIOD_COUNTER
        all_users_average_message = "All users average in the past %(seconds)s seconds is %(average)s" % {
            "seconds": str(PERIOD_DURATION),
            "average": str(all_users_average),
        }
        outputs.append([LAST_CHANNEL_TO_SEND_MESSAGE, all_users_average_message])

    CURRENT_PERIOD_COUNTER = 0
    CURRENT_PERIOD_SUM = 0.0


@route('/average/')
def average():
    global ALL_USERS_COUNTER
    global ALL_USERS_SUM

    if ALL_USERS_COUNTER == 0:
        return NO_NUMBERS_WRITTEN_YET
    average_string = str(ALL_USERS_SUM / ALL_USERS_COUNTER)
    return average_string


@route('/average/<username_to_search>')
def average_user(username_to_search, slack_client=sc):
    global AVERAGE_PER_USER_DICT

    slack_user_id = None

    if AVERAGE_PER_USER_DICT.get(username_to_search, False):
        slack_user_id = username_to_search
    else:

        try:
            api_response = slack_client.api_call("users.list")
        except Exception:
            return NO_SUCH_USER_FOUND

        if api_response.get('ok', False):
            all_channel_users = [user for user in api_response['members'] if user.get('name', None) == username_to_search]
            if len(all_channel_users) == 1:
                found_user = all_channel_users[0]
                slack_user_id = found_user.get('id', None) # If the user is not found
            elif len(all_channel_users) > 0:
                return MORE_THAN_ONE_USER_BE_MORE_SPECIFIC

    if slack_user_id and slack_user_id in AVERAGE_PER_USER_DICT:
        users_average = AVERAGE_PER_USER_DICT[slack_user_id]['total'] / AVERAGE_PER_USER_DICT[slack_user_id]['counter']
        return str(users_average)

    return NO_SUCH_USER_FOUND


# Management methods for starting the server asynchronously
def _start_webserver_async():
    run(host='localhost', port=8080, server='paste')

webserver_thread = Thread(group=None, target=_start_webserver_async)
webserver_thread.start()

