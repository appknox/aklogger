from unittest import TestCase
from .. import aklogger
import os


class TestAKLogger(TestCase):

    def setUp(self):
        self.logger = aklogger.AKLogger('test')
        self.handler = aklogger.handlers.FileHandler('test.log')
        self.logger.add_handler(self.handler)

    def tearDown(self):
        os.remove('test.log')

    def test_file_handler(self):
        title = 'Testing FileHandler Title'
        desc = 'Testing FileHandler Desc'

        message = '{}{}{}'.format(title, '\n\n', desc)
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
        msg1 = 'Testing logger.info'
        self.logger.info(msg1)

        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)

        self.assertEqual(msg1, content2.strip())

    def test_warning(self):
        # Test logger.info
        msg1 = 'Testing logger.info'
        self.logger.warning('', msg1)
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)

        self.assertEqual(msg1, content2.strip())

    def test_error(self):
        # Test logger.info
        self.logger.error('', '')
        with open('test.log', 'r+') as f:
            content2 = f.read()
            f.truncate(0)
        self.assertEqual('', content2.strip())

    def test_critical(self):
        # Test logger.info
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

    def test_remove_handler(self):
        self.logger.remove_handler(self.handler)
        has_handler = self.logger.has_handlers()
        self.assertFalse(has_handler)
