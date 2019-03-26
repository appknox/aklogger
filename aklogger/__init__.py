import logging

from slacker import Slacker

tpl = """
=====================
{summary}
---------------------
{details}
=====================
"""

root_logger = logging.getLogger('root')
root_stream_handler = logging.StreamHandler()

try:
    from celery.utils.log import get_task_logger
    root_logger = get_task_logger('root')
except ImportError:
    pass

root_logger.addHandler(root_stream_handler)

try:
    from celery.signals import after_setup_task_logger, after_setup_logger

    @after_setup_logger.connect
    def after_setup_aklogger(logger, *args, **kwargs):
        root_logger.removeHandler(root_stream_handler)

    @after_setup_task_logger.connect
    def after_setup_task_aklogger(logger, *args, **kwargs):
        root_logger.removeHandler(root_stream_handler)
except ImportError:
    pass


def get_logger(name):
    return root_logger.getChild(name)


CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARNING = logging.WARNING
INFO = logging.INFO
DEBUG = logging.DEBUG
NOTSET = logging.NOTSET

_levelToName = {
    CRITICAL: 'CRITICAL',
    ERROR: 'ERROR',
    WARNING: 'WARNING',
    INFO: 'INFO',
    DEBUG: 'DEBUG',
    NOTSET: 'NOTSET',
}

_levelToColor = {
    ERROR: 'danger',
    WARNING: 'warning',
    INFO: '#439FE0',
    DEBUG: '#808080',
}


class AKLogger(object):

    def __init__(self, name, parent=None):
        self.set_name(name)
        self.parent = parent
        self.logger = get_logger(self.get_name())
        self.slkr = None
        self.slack_token = None
        self.slack_level = None
        self.setLevel(NOTSET)

    def set_name(self, name):
        self.name = name

    def get_name(self):
        if self.parent is not None:
            return self.parent.get_name() + ':' + self.name
        return self.name

    def getLogger(self, name):
        return AKLogger(name, parent=self)

    def setLevel(self, level):
        self.level = logging._checkLevel(level)
        self.logger.setLevel(self.level)

    def getLevel(self):
        return self.level

    def enable_slack(self, token):
        self.slkr = Slacker(token)
        self.slkr.api.test()
        self.slack_token = token

    def disable_slack(self):
        self.slkr = None
        self.slack_token = None

    def get_slack_level(self):
        return self.slack_level or self.level

    def set_slack_level(self, level):
        self.slack_level = logging._checkLevel(level)

    def log_to_file(self, file_name):
        self.filename = file_name
        handler = logging.FileHandler(self.filename)
        self.logger.addHandler(handler)

    def debug(self, summary, details=None, channel='#error',
              force_push_slack=False, *args, **kwargs):
        self._log(DEBUG, self.get_name(), summary, details, channel,
                  force_push_slack, *args, **kwargs)

    def info(self, summary, details=None, channel='#error',
             force_push_slack=False, *args, **kwargs):
        self._log(INFO, self.get_name(), summary, details, channel,
                  force_push_slack, *args, **kwargs)

    def warning(self, summary, details=None, channel='#error',
                force_push_slack=False, *args, **kwargs):
        self._log(WARNING, self.get_name(), summary, details, channel,
                  force_push_slack, *args, **kwargs)

    def error(self, summary, details=None, channel='#error',
              force_push_slack=False, *args, **kwargs):
        self._log(ERROR, self.get_name(), summary, details, channel,
                  force_push_slack, *args, **kwargs)

    def _log(self, level, name, summary=None, details=None, channel='#error',
             force_push_slack=False, *args, **kwargs):

        if self.parent:
            self.parent._log(level, name, summary, details, channel,
                             force_push_slack, *args, **kwargs)

        if level < self.getLevel() or self.getLevel() == NOTSET:
            return

        msg = summary
        if details:
            msg = tpl.format(
                summary=summary,
                details=details
            )
        method_to_call = getattr(self.logger, _levelToName.get(level).lower())
        method_to_call(msg, *args, **kwargs)
        if force_push_slack or self.should_push_to_slack(level):
            self.slack_push(summary, details, channel, level)

    def get_slack_color(self, level):
        color = _levelToColor.get(level, _levelToColor[10])
        return color

    def should_push_to_slack(self, level):
        if not self.slkr:
            return False
        if level < self.get_slack_level():
            return False
        return True

    def slack_push(self, summary, details, channel, level):
        try:
            self.slkr.chat.post_message(
                channel=channel,
                text=summary,
                username=self.name,
                icon_emoji=':squirrel:',
                attachments=[
                    {
                        'fallback': summary,
                        'text': details,
                        'color': self.get_slack_color(level),
                    }
                ] if details else None,
            )
        except Exception as e:
            self.logger.error('Slack failed: {}'.format(e))


logger = AKLogger('root')


def getLogger(name=None):
    if name is None:
        return logger
    return logger.getLogger(name)
