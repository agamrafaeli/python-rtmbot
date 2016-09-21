# Average Counter Chat Bot

## General Architecture
The entire solution to the task has been done as a plugin for the **python-rtmbot** framework. Thus the entire solution can be found inside a fork of **python-rtmbot** inside the [plugins folder](https://github.com/agamrafaeli/python-rtmbot/tree/master/plugins/average_counter_bot "Agam's task solution in the python-rtmbot folder"). The solution has four files:
- `README.md` - This file
- `requirements.txt` - Has all of the requirements of python-rtmbot at the time of writing this plugin and all of the required packages for the Average Counter Chat Bot (bottle and mock)
- `average_counter_bot.py` - The actual code solution of the bot, with the message handling, timed report back to the public channel and web view
- `test_average_counter.py` - Unit tests for Average Counter Chat Bot's code

To run the bot you follow all of the instructions like for **python-rtmbot**, except run
```shell
pip install -r plugins/average_counter_bot/requirements.txt
```
and only then:
```shell
python rtmbot.py
```

## Setup
### Configuration variables
- `PERIOD_DURATION` - Is used to define every how often a report is posted on the average of all the users numbers in the previous period seconds.

### Internal management variables
I have two sets of (sum, counter) variables. 
- `CURRENT_PERIOD` - Used for the current period to be ommitted every minute onto the last public channel that had a message.
- `ALL_USERS` - Used for summing all of the users activity so that the average can be displayed in the bot's web view
- `LAST_CHANNEL_TO_SEND_MESSAGE` - Saves the ID of the last channel that sent a message. This is used to decide to which channel to send the report every minute on the overall average in the last time period.
- `AVERAGE_PER_USER_DICT` - A dictionary where the key is the user's Slack ID and the value is another dictionary with the keys:
    - `total` - sums all of the numbers the user enters
    - `counter` - is init-ed to 0, and incremented by one each time the user adds a number.


### String Constants
- `MORE_THAN_ONE_USER_BE_MORE_SPECIFIC` - To be displayed when `/average/<username>` is called and more than one user is returned from Slack that matches this query string.
- `NO_SUCH_USER_FOUND` - To be displayed when `/average/<username>` is called and no user is found matching the given query.
- `NO_NUMBERS_WRITTEN_YET` - To be displayed when `/average/` is called and no number has been written since the bot started running.

## Last words
I hope you will have as much fun checking this task as I did writing it.
