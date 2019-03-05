import json
import traceback
from logging import (
    Handler,
    StreamHandler,
    FileHandler,
    CRITICAL,
    ERROR,
    WARNING,
    INFO,
    FATAL,
    DEBUG,
    NOTSET,
    Formatter)

from django.utils.log import AdminEmailHandler
from slacker_log_handler import SlackerLogHandler as SlackLogHandler


class SlackerLogHandler(SlackLogHandler):

    def slack_alert(self, summary, details, channel, color='good'):
        if settings.DISABLE_SLACK:
            return
        if not settings.DEBUG:
            slkr = slacker.Slacker(settings.SLACK_TOKEN)
            slkr.chat.post_message(
                channel=channel,
                text=summary,
                username='Mycroft',
                icon_emoji=':squirrel:',
                attachments=[
                    {
                        'fallback': summary,
                        'text': details,
                        'color': color,
                    }
                ] if details else None,
            )


    def slack_error(self, summary, details=None):
        logger.error(summary)
        if details:
            logger.error(details)
        slack_alert(
            summary, details, channel=settings.SLACK_ERROR_CHANNEL, color='danger')


    def slack_warning(self, summary, details=None):
        logger.warning(summary)
        if details:
            logger.warning(details)
        slack_alert(
            summary, details, channel=settings.SLACK_ERROR_CHANNEL, color='warning')


    def slack_info(self, summary, details=None):
        logger.info(summary)
        if details:
            logger.info(details)
        slack_alert(
            summary, details, channel=settings.SLACK_ERROR_CHANNEL, color='good')


FileHandler = FileHandler
StreamHandler = StreamHandler
AdminEmailHandler = AdminEmailHandler
SlackerLogHandler = SlackerLogHandler
