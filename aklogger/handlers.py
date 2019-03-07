import logging

import json
from logging import (
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    FATAL,
    DEBUG,
    NOTSET,
    Formatter,
)

import six
import slacker

from . import utils

ERROR_COLOR = 'danger'  # color name is built in to Slack API
WARNING_COLOR = 'warning'  # color name is built in to Slack API
INFO_COLOR = '#439FE0'

COLORS = {
    CRITICAL: ERROR_COLOR,
    FATAL: ERROR_COLOR,
    ERROR: ERROR_COLOR,
    WARNING: WARNING_COLOR,
    INFO: INFO_COLOR,
    DEBUG: INFO_COLOR,
    NOTSET: INFO_COLOR,
}

DEFAULT_EMOJI = ':heavy_exclamation_mark:'


class NoStacktraceFormatter(Formatter):
    """
    By default the stacktrace will be formatted as part of the message.
    Since we want the stacktrace to be in the attachment of the Slack
    message, we need a custom formatter to leave it out of the message.
    """

    def formatException(self, ei):
        return None


class SlackerLogHandler(logging.Handler):

    def __init__(self, api_key, channel, stack_trace=True,
                 username='Python logger', icon_url=None, icon_emoji=None,
                 fail_silent=False, ping_users=None, ping_level=None):
        logging.Handler.__init__(self)
        self.formatter = NoStacktraceFormatter()

        self.stack_trace = stack_trace
        self.fail_silent = fail_silent

        self.slacker = slacker.Slacker(api_key)

        self.username = username
        self.icon_url = icon_url
        if (icon_emoji or icon_url):
            self.icon_emoji = icon_emoji
        else:
            self.icon_emoji = DEFAULT_EMOJI
        self.channel = channel
        channel1 = self.channel.startswith('#')
        channel2 = self.channel.startswith('@')
        if not channel1 and not channel2:
            self.channel = '#' + self.channel

        self.ping_level = ping_level
        self.ping_users = []

        if ping_users:
            user_list = self.slacker.users.list().body['members']

            for ping_user in ping_users:
                ping_user = ping_user.lstrip('@')

                for user in user_list:
                    if user['name'] == ping_user:
                        self.ping_users.append(user['id'])
                        break
                else:
                    raise RuntimeError(
                        'User not found in Slack users list: %s' % ping_user)

    def build_msg(self, record):
        return six.text_type(self.format(record))

    def build_trace(self, record, fallback, text):
        trace = {
            'fallback': fallback,
            'text': text,
            'color': COLORS.get(self.level, INFO_COLOR)
        }
        return trace

    def emit(self, record):
        message = self.build_msg(record)
        message_list = message.split(utils.MESSAGE_SEPERATOR, 1)
        if len(message_list) == 2:
            title = message_list[0]
            description = message_list[1]
        else:
            title = message_list[0]
            description = None

        if self.ping_users and record.levelno >= self.ping_level:
            for user in self.ping_users:
                message = '<@{}> {}'.format(user, title)

        if self.stack_trace:
            trace = self.build_trace(record, fallback=title, text=description)
            attachments = json.dumps([trace])
        else:
            attachments = None
        try:
            self.slacker.chat.post_message(
                text=title,
                channel=self.channel,
                username=self.username,
                icon_url=self.icon_url,
                icon_emoji=self.icon_emoji,
                attachments=attachments,
            )
        except slacker.Error as e:
            if self.fail_silent:
                pass
            else:
                raise e


class FileHandler(logging.FileHandler):
    pass


class StreamHandler(logging.StreamHandler):
    pass
