from unittest import TestCase
from .. import aklogger
import os
import slacker


class TestAKLogger(TestCase):

    def setUp(self):
        self.logger = aklogger.AKLogger('test')
        self.handler = aklogger.handlers.FileHandler('test.log')
        self.logger.add_handler(self.handler)

    def tearDown(self):
        os.remove('test.log')

    def test_file_handler(self):
        title = 'title'
        desc = 'desc'
        message = '{}{}{}'.format(title,
                                  aklogger.utils.MESSAGE_SEPERATOR,
                                  desc)
        g_message = aklogger.utils.get_message(title, desc)

        # Test utils.get_message
        self.assertEqual(message, g_message)

        self.logger.debug(title, desc)

        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)

        # Test FileHandler
        self.assertEqual(message, content1.strip())

    def test_info(self):
        # Test logger.info
        title = 'Testing logger.info'
        self.logger.info(title, None)
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)
        self.assertEqual(title, content2.strip())

    def test_warning(self):
        # Test logger.warning
        msg1 = 'Testing logger.warning'
        self.logger.warning(None, msg1)
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)
        self.assertEqual(msg1, content2.strip())

    def test_error(self):
        # Test logger.error
        self.logger.error('', '')
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)
        self.assertEqual('', content2.strip())

    def test_critical(self):
        # Test logger.critical
        msg = 'Testing critical'
        self.logger.critical(msg)
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)
        self.assertEqual(msg, content2.strip())

    def test_has_handlers(self):
        # Test has_handlers
        has_handler = self.logger.has_handlers()
        self.assertTrue(has_handler)

    def test_set_level(self):
        self.logger.set_level('INFO')
        msg = 'Testing set_level'
        self.logger.debug(msg)

        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        # Test FileHandler
        self.assertEqual('', content1.strip())

    def test_console_formatter(self):
        formatter = aklogger.formatters.console_formatter
        self.handler.setFormatter(formatter)
        msg = 'testing console_formatter'
        output_message = 'test        : ERROR    testing console_formatter'
        self.logger.error(msg)
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual(output_message, content1.strip())

    def test_unicode_input(self):
        # Test tab
        msg1 = '\u0009'
        self.logger.error(msg1)
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('\t\n', content1)

        # Test dollar
        msg2 = '\u0024'
        self.logger.error(msg2)
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('$', content1.strip())

    def test_no_input(self):
        self.logger.error()
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('', content1)

    def test_none_input(self):
        title = None
        desc = None
        self.logger.error(title, desc)
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('', content1)

    def test_multiple_new_lines_input(self):
        title = '\n\n\n\n\n\n'
        desc = 'desc'
        self.logger.error(title, desc)
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('\n\n\n\n\n\n{}desc\n'
                         .format(aklogger.utils.MESSAGE_SEPERATOR),
                         content1)

    def test_remove_handler(self):
        self.logger.remove_handler(self.handler)
        self.logger.error('title')
        with open('test.log', 'r+') as f:
            content1 = f.read()
            f.truncate(0)
        self.assertEqual('', content1)

    def test_slack_handler(self):
        self.logger.remove_handler(self.handler)

        token = 'invalid token'
        channel = 'invalid channel'

        self.handler = aklogger.handlers.SlackerLogHandler(token, channel)
        self.logger.add_handler(self.handler)

        with self.assertRaises(slacker.Error):
            self.logger.error('title', 'desc')

        with self.assertRaises(slacker.Error):
            aklogger.handlers.SlackerLogHandler(token,
                                                channel,
                                                ping_users=['sks'])
