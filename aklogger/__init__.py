import logging

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


tpl = """
=====================
{summary}
---------------------
{details}
=====================
"""

root_logger = logging.getLogger("root")
root_stream_handler = logging.StreamHandler()

try:
    from celery.utils.log import get_task_logger

    root_logger = get_task_logger("root")
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
    CRITICAL: "CRITICAL",
    ERROR: "ERROR",
    WARNING: "WARNING",
    INFO: "INFO",
    DEBUG: "DEBUG",
    NOTSET: "NOTSET",
}

_levelToColor = {
    ERROR: "danger",
    WARNING: "warning",
    INFO: "#439FE0",
    DEBUG: "#808080",
}


class AKLogger(object):
    def __init__(self, name: str, parent: "AKLogger" = None) -> None:
        self.set_name(name)
        self.parent = parent
        self.logger = get_logger(self.get_name())

        self.slack_client = None
        self.slack_token = None
        self.slack_level = None
        self.slack_channel = None
        self.slack_icon_emoji = ":shipit:"

        self.setLevel(NOTSET)

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        if self.parent is not None:
            return self.parent.get_name() + ":" + self.name
        return self.name

    def getLogger(self, name: str) -> "AKLogger":
        return AKLogger(name, parent=self)

    def setLevel(self, level: str) -> None:
        self.level = logging._checkLevel(level)
        self.logger.setLevel(self.level)

    def getLevel(self) -> str:
        return self.level

    def enable_slack(self, token: str, channel: str) -> None:
        self.slack_client = WebClient(token=token)
        api_response = self.slack_client.api_test()
        self.logger.debug(f"aklogger: Slack API test ok: {api_response['ok']}")

        self.slack_token = token
        self.slack_channel = channel

    def disable_slack(self) -> None:
        self.slack_client = None
        self.slack_token = None
        self.slack_channel = None

    def get_slack_level(self) -> str:
        return self.slack_level or self.level

    def set_slack_level(self, level: str) -> None:
        self.slack_level = logging._checkLevel(level)

    def set_slack_preferences(self, icon_emoji: str) -> None:
        self.slack_icon_emoji = icon_emoji

    def log_to_file(self, file_name: str) -> None:
        self.filename = file_name
        handler = logging.FileHandler(self.filename)
        self.logger.addHandler(handler)

    def debug(
        self,
        summary: str,
        details: str = None,
        slack_channel: str = None,
        force_push_slack: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self._log(
            DEBUG,
            self.get_name(),
            summary,
            details,
            slack_channel,
            force_push_slack,
            *args,
            **kwargs,
        )

    def info(
        self,
        summary: str,
        details: str = None,
        slack_channel: str = None,
        force_push_slack: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self._log(
            INFO,
            self.get_name(),
            summary,
            details,
            slack_channel,
            force_push_slack,
            *args,
            **kwargs,
        )

    def warning(
        self,
        summary: str,
        details: str = None,
        slack_channel: str = None,
        force_push_slack: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self._log(
            WARNING,
            self.get_name(),
            summary,
            details,
            slack_channel,
            force_push_slack,
            *args,
            **kwargs,
        )

    def error(
        self,
        summary: str,
        details: str = None,
        slack_channel: str = None,
        force_push_slack: bool = False,
        *args,
        **kwargs,
    ) -> None:
        self._log(
            ERROR,
            self.get_name(),
            summary,
            details,
            slack_channel,
            force_push_slack,
            *args,
            **kwargs,
        )

    def _log(
        self,
        level: str,
        name: str,
        summary: str = None,
        details: str = None,
        slack_channel: str = None,
        force_push_slack: bool = False,
        *args,
        **kwargs,
    ) -> None:
        if self.parent:
            self.parent._log(
                level,
                name,
                summary,
                details,
                slack_channel,
                force_push_slack,
                *args,
                **kwargs,
            )

        if level < self.getLevel() or self.getLevel() == NOTSET:
            return

        msg = summary
        if details:
            msg = tpl.format(summary=summary, details=details)
        method_to_call = getattr(self.logger, _levelToName.get(level).lower())
        method_to_call(msg, *args, **kwargs)
        if force_push_slack or self.should_push_to_slack(level):
            self.slack_push(summary, details, slack_channel, level)

    def get_slack_color(self, level: str) -> str:
        color = _levelToColor.get(level, _levelToColor[10])
        return color

    def should_push_to_slack(self, level: str) -> bool:
        if self.slack_client is None:
            return False
        if level < self.get_slack_level():
            return False
        return True

    def slack_push(
        self, summary: str, details: str, channel: str, level: str
    ) -> None:
        if not channel:
            channel = self.slack_channel

        try:
            response = self.slack_client.chat_postMessage(
                channel=channel,
                text=summary,
                username=self.name,
                icon_emoji=self.slack_icon_emoji,
                attachments=[
                    {
                        "fallback": summary,
                        "text": details,
                        "color": self.get_slack_color(level),
                    }
                ]
                if details
                else None,
            )
            assert response["message"]["text"] == summary
        except SlackApiError as e:
            assert e.response["ok"] is False
            error_response = e.response["error"]
            assert error_response
            self.logger.error(f"aklogger: Slack push failed: {error_response}")


logger = AKLogger("root")


def getLogger(name: str = None) -> AKLogger:
    if name is None:
        return logger
    return logger.getLogger(name)
