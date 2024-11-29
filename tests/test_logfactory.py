import logging.handlers
from unittest import TestCase, main  # mock
import os
import logging
from logging_sandbox import logfactory
import logging_sandbox


class TestLogfactory(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.logger = logfactory.create_logger()

    def tearDown(self) -> None:
        if self.logger.hasHandlers():
            while len(self.logger.handlers) > 0:
                h = self.logger.handlers[0]
                self.logger.removeHandler(h)
        self.assertFalse(self.logger.hasHandlers(),
                         "handlers not removed")
        return super().tearDown()

    def setUp(self) -> None:
        return super().setUp()

    def test_create_logger(self):
        self.assertIsInstance(self.logger, logging.Logger,
                              "Did not create logger object")
        self.assertEqual(self.logger.name, logging_sandbox.__name__,
                         "logger.name not equal to package name")

    def test_set_consoleHandler(self):
        logfactory.set_consoleHandler(self.logger, "INFO",
                                      "testconsole")
        self.assertTrue(self.logger.hasHandlers(),
                        "no handler found")
        handler = self.logger.handlers[0]
        self.assertIsInstance(handler, logging.StreamHandler,
                              "handler is not a logging.StreamHandler")
        self.assertEqual(handler.name, "testconsole",
                         "name of streamhandler incorrect")
        self.assertEqual(handler.level, logging.INFO,
                         "loglevel of streamhandler incorrect")

    def test_set_fileHandler(self):
        filename = "filehandler_test.log"
        handlername = "testfile"
        logfactory.set_fileHandler(self.logger, filename, "INFO",
                                   handlername)
        self.assertTrue(self.logger.hasHandlers(),
                        "no handler found")
        handler = self.logger.handlers[0]
        self.assertIsInstance(handler, logging.FileHandler,
                              "handler is not a logging.FileHandler")
        self.assertEqual(handler.name, "testfile",
                         "name of handler incorrect")
        self.assertEqual(handler.level, logging.INFO,
                         "loglevel of handler incorrect")
        self.assertTrue(os.path.isfile(filename),
                        "log file not created")
        handler.close()
        os.remove(filename)

    def test_get_handlers_by_name(self):
        handlernames = ["handler1", "handler2"]
        for hn in handlernames:
            logfactory.set_consoleHandler(self.logger, "INFO", hn)
        handlers = logfactory.get_handlers_by_name(self.logger)
        self.assertIsInstance(handlers, dict, "handlers not a dict")
        self.assertEqual(len(handlers), len(handlernames),
                         "number of handlers not equal to number of names")
        for hn in handlernames:
            self.assertIn(hn, handlers.keys(),
                          "handler name not found in handlers")
            self.assertIsInstance(handlers[hn], list,
                                  "handler not a list")
            self.assertEqual(len(handlers[hn]), 1,
                             "handler list not of length 1")

    def test_get_duplicate_handlers(self):
        handlernames = ["handler1", "handler2", "handler2"]
        for hn in handlernames:
            logfactory.set_consoleHandler(self.logger, "INFO", hn)
        handlers = logfactory.get_duplicate_handlers(self.logger)
        self.assertIsInstance(handlers, dict, "handlers not a dict")
        self.assertEqual(len(handlers), 1,
                         "number of duplicate handlers not equal to 1")
        self.assertIn("handler2", handlers.keys(),
                      "handler name not found in handlers")
        self.assertNotIn("handler1", handlers.keys(),
                         "handler name found in handlers")
        self.assertIsInstance(handlers["handler2"], list,
                              "handler not a list")
        self.assertEqual(len(handlers["handler2"]), 2,
                         "handler list not of length 2")

    def test_remove_duplicate_handlers(self):
        handlernames = ["handler1", "handler2", "handler2"]
        for hn in handlernames:
            logfactory.set_consoleHandler(self.logger, "INFO", hn)
        self.assertEqual(len(self.logger.handlers), 3,
                         "number of handlers not equal to 3, setting failed")
        logfactory.remove_duplicate_handlers(self.logger)
        self.assertTrue(self.logger.hasHandlers(),
                        "no handler found")
        self.assertEqual(len(self.logger.handlers), 2,
                         "number of handlers not equal to 2, removal failed")
        handlers = logfactory.get_duplicate_handlers(self.logger)
        self.assertEqual(len(handlers), 0,
                         "duplicate handlers not removed")


if __name__ == "__main__":
    main()
