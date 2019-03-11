import logging
from aklogger import logger


class DjangoHandler(logging.Handler):

    def __init__(self, name, slack_token=None,
                 slack_level=logging.ERROR, filename=None):
        super().__init__()
        logger.set_name(name)
        if slack_token:
            logger.enable_slack(slack_token)
        logger.set_slack_level(slack_level)
        if filename:
            logger.log_to_file(filename)

    def setLevel(self, level):
        logger.setLevel(level)
        super(DjangoHandler, self).setLevel(level)

    def emit(self, record):
        method_to_call = getattr(logger, record.levelname.lower())
        method_to_call(record.getMessage())
