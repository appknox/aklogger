import logging
from . import formatters, handlers, utils # noqa


class AKLogger(object):

    def __init__(self, name='root', level=None, **kwargs):
        self.logger = logging.Logger(name)
        if level:
            self.logger.setLevel(level)
        handler = kwargs.get('handler')
        formatter = kwargs.get('formatter', formatters.basic_formatter)
        if handler:
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def set_level(self, level):
        return self.logger.setLevel(level)

    def debug(self, title=None, msg=None):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.debug(message)

    def info(self, title=None, msg=None):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.info(message)

    def warning(self, title=None, msg=None):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.warning(message)

    def error(self, title=None, msg=None):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.error(message)

    def critical(self, title=None, msg=None):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.critical(message)

    def add_handler(self, hldr):
        return self.logger.addHandler(hldr)

    def remove_handler(self, hldr):
        return self.logger.removeHandler

    def has_handlers(self):
        return self.logger.hasHandlers
