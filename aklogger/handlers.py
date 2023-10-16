import logging
from aklogger import logger


class DjangoHandler(logging.Handler):
    def __init__(
        self,
        name,
        slack_token=None,
        slack_level=logging.ERROR,
        slack_channel="#error",
        slack_icon_emoji=":shipit:",
        filename=None,
    ):
        super().__init__()
        logger.set_name(name)
        if slack_token:
            logger.enable_slack(token=slack_token, channel=slack_channel)
        logger.set_slack_preferences(icon_emoji=slack_icon_emoji)
        logger.set_slack_level(slack_level)
        if filename:
            logger.log_to_file(filename)

    def setLevel(self, level):
        logger.setLevel(level)
        super(DjangoHandler, self).setLevel(level)

    def emit(self, record):
        method_to_call = getattr(logger, record.levelname.lower())
        method_to_call(record.getMessage())
