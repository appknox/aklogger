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


class AKLogger(object):

    def __init__(self, name, parent=None):
        self.set_name(name)
        self.parent = parent
        self.logger = get_logger(self.get_name())
        self.slkr = None
        self.slack_token = None
        self.setLevel(WARNING)

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
              *args, **kwargs):
        self._log(DEBUG, summary, details, channel, *args, **kwargs)

    def info(self, summary, details=None, channel='#error', *args,
             **kwargs):
        self._log(INFO, summary, details, channel, *args, **kwargs)

    def warning(self, summary, details=None, channel='#error', *args,
                **kwargs):
        self._log(WARNING, summary, details, channel, *args, **kwargs)

    def error(self, summary, details=None, channel='#error', *args,
              **kwargs):
        self._log(ERROR, summary, details, channel, *args, **kwargs)

    def _log(self, level, summary=None, details=None, channel='#error',
             *args, **kwargs):
        msg = summary
        if details:
            msg = tpl.format(
                summary=summary,
                details=details
            )
        method_to_call = getattr(self.logger, _levelToName.get(level).lower())
        method_to_call(msg, *args, **kwargs)
        self.slack_alert(summary, details, channel, level)

    def slack_alert(self, summary, details, channel, level,
                    color='good'):
        if not self.slkr:
            return
        if level < self.slack_level:
            return
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
                        'color': color,
                    }
                ] if details else None,
            )
        except Exception as e:
            self.logger.error('Slack failed: {}'.format(e))


logger = AKLogger('root')


def getLogger(name=None):
    if name is None:
        return logger
    return AKLogger(name)
