from slack_sdk.errors import SlackApiError

from aklogger import logger


class TestAkLogger:
    logger.set_name("mycroft")
    try:
        logger.enable_slack("invalid_token", "#test_channel_name")
    except SlackApiError:
        pass
    logger.setLevel("DEBUG")
    logger.set_slack_level("WARNING")
    logger.log_to_file("file.log")

    slack_invalid_auth_error = (
        "aklogger: Slack push failed: The request to the Slack API failed. "
        "(url: https://www.slack.com/api/chat.postMessage)\n"
        "The server responded with: {'ok': False, 'error': 'invalid_auth'}"
    )

    def test_debug_should_write_if_loglevel_is_debug(self):
        summary = "This is a debug message"
        details = "This is the details of the debug message"

        logger.setLevel("DEBUG")
        logger.debug(summary, details)

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "\n====================="
            "\nThis is a debug message"
            "\n---------------------"
            "\nThis is the details of the debug message"
            "\n====================="
            "\n\n"
        )

    def test_debug_should_not_write_if_loglevel_is_above_debug(self):
        logger.setLevel("INFO")
        logger.debug("debug message text")

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == ""

    def test_info_should_write_if_loglevel_is_info_or_below(self):
        summary = "This is an info message"
        details = "This is the details of the info message"
        # logger.setLevel("INFO")
        logger.info(summary, details)

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "\n====================="
            "\nThis is an info message"
            "\n---------------------"
            "\nThis is the details of the info message"
            "\n====================="
            "\n\n"
        )

    def test_info_should_not_write_if_loglevel_is_above_info(self):
        logger.setLevel("WARN")
        logger.info("info message text")

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == ""

    def test_warning_should_write_if_loglevel_is_warning_or_below(self):
        summary = "This is a warning message"
        details = "This is the details of the warning message"
        logger.setLevel("WARN")
        logger.warning(summary, details)

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "\n====================="
            "\nThis is a warning message"
            "\n---------------------"
            "\nThis is the details of the warning message"
            "\n====================="
            "\n"
            f"\n{self.slack_invalid_auth_error}\n"
        )

    def test_warning_should_not_write_if_loglevel_is_above_warn(self):
        logger.setLevel("ERROR")
        logger.warning("warning message text")

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == ""

    def test_error_should_write_if_loglevel_is_error(self):
        summary = "This is an error message"
        details = "This is the details of the error message"
        logger.setLevel("ERROR")
        logger.error(summary, details)

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "\n====================="
            "\nThis is an error message"
            "\n---------------------"
            "\nThis is the details of the error message"
            "\n====================="
            "\n"
            f"\n{self.slack_invalid_auth_error}\n"
        )

    def test_should_render_text_if_only_summary_is_provided(self):
        logger.setLevel("ERROR")
        logger.error("Sample error summary")

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "Sample error summary" f"\n{self.slack_invalid_auth_error}\n"
        )

    def test_should_render_template_if_only_summary_and_details_are_provided(
        self,
    ):
        logger.setLevel("ERROR")
        logger.error("summary text", "details text")

        with open("file.log", "r+") as f:
            file_log = f.read()
            f.truncate(0)

        assert file_log == (
            "\n====================="
            "\nsummary text"
            "\n---------------------"
            "\ndetails text"
            "\n====================="
            "\n"
            f"\n{self.slack_invalid_auth_error}\n"
        )
