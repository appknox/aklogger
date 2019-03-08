import logging
from . import formatters, handlers, utils


class AKLogger(object):

    def __init__(self, name='root', level=None, **kwargs):
        self.logger = logging.Logger(name)
        self.handler = kwargs.get('handler', handlers.StreamHandler())
        self.formatter = kwargs.get('formatter', formatters.basic_formatter)
        if not level:
            self.level = 'DEBUG'
        self.handler.setLevel(self.level)
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    def set_level(self, level):
        return self.logger.setLevel(level)

    def debug(self, title=None, msg=None, *args, **kwargs):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.debug(message)

    def info(self, title=None, msg=None, *args, **kwargs):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.info(message)

    def warning(self, title=None, msg=None, *args, **kwargs):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.warning(message)

    def error(self, title=None, msg=None, *args, **kwargs):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.error(message)

    def critical(self, title=None, msg=None, *args, **kwargs):
        message = utils.get_message(title, msg)
        if not message:
            return
        return self.logger.critical(message)

    def add_handler(self, hldr):
        return self.logger.addHandler(hldr)

    def remove_handler(self, hldr):
        return self.logger.removeHandler(hldr)

    def has_handlers(self):
        return self.logger.hasHandlers()
