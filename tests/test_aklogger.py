import os
from aklogger import logger, tpl
import slacker

logger.set_name('mycroft')
try:
    logger.enable_slack('invalid_token')
except slacker.Error:
    pass
logger.setLevel('DEBUG')
logger.set_slack_level('WARNING')
logger.log_to_file('file.log')


def test_debug():
    title = 'This is a debug message'
    desc = 'This is the description of the debug message'
    logger.debug(title, desc, '#error')
    msg = tpl.format(
        summary=title,
        details=desc
    )
    with open('file.log', 'r+') as f:
        content = f.read()
        f.truncate(0)
    assert len(msg) + 1 == len(content)


def test_info():
    title = 'This is a info message'
    desc = 'This is the description of the info message'
    logger.info(title, desc, '#error')
    msg = tpl.format(
        summary=title,
        details=desc
    )
    with open('file.log', 'r+') as f:
        content = f.read()
        f.truncate(0)
    assert len(msg) + 1 == len(content)


def test_warning():
    title = 'This is a warning message'
    desc = 'This is the description of the warning message'
    logger.warning(title, desc, '#error')
    msg = tpl.format(
        summary=title,
        details=desc
    )
    # extra_slack_log_for_invalid_token_or_channel
    extra_log = 'Slack failed: invalid_auth'
    msg2 = msg + '\n' + extra_log
    with open('file.log', 'r+') as f:
        content = f.read()
        f.truncate(0)
    assert len(msg2) + 1 == len(content)


def test_error():
    title = 'This is a error message'
    desc = None
    logger.error(title, desc, '#error')
    # extra_slack_log_for_invalid_token_or_channel
    extra_log = 'Slack failed: invalid_auth'
    msg2 = title + '\n' + extra_log
    with open('file.log', 'r+') as f:
        content = f.read()
        f.truncate(0)
    assert len(msg2) + 1 == len(content)
    os.remove('file.log')
