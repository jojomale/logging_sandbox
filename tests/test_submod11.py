from unittest import TestCase, main, mock
import os
import shutil
from logging_sandbox import logfactory
from logging_sandbox.module1 import submod11
import logging_sandbox
from datetime import datetime


class TestSampleClass(TestCase):
    def setUp(self) -> None:
        self.outputdir = "output"
        self.parent_logger = logfactory.create_logger()
        self.exec_time = datetime(2021, 1, 1, 0, 0, 0)
        self.logfilename = os.path.join(
            self.outputdir, submod11.LOGDIR,
            ('correlate%srank' + submod11.RANK_STRFMT) % (
             self.exec_time.strftime(submod11.LOG_TSTRFMT), 0))
        self.loglevel = "CRITICAL"
        return super().setUp()

    def tearDown(self) -> None:
        if os.path.isdir(self.outputdir):
            shutil.rmtree(self.outputdir)
        return super().tearDown()

    @mock.patch("logging_sandbox.module1.submod11.datetime")
    def test_logfile_creation(self, mock_time):
        mock_time.now.return_value = self.exec_time
        sc = submod11.SampleClass(self.loglevel, self.outputdir)
        self.assertEqual(sc.logger.parent, self.parent_logger)
        self.assertEqual(sc.logger.parent.name, logging_sandbox.__name__,
                         "Name of parent logger of SampleClass is package name"
                         )
        self.assertTrue(os.path.isfile(self.logfilename),
                        "Log file created")

    @mock.patch("logging_sandbox.module1.submod11.os.makedirs")
    @mock.patch("logging_sandbox.module1.submod11.datetime")
    @mock.patch("logging_sandbox.module1.submod11.logfactory.set_fileHandler")
    def test_handler_check(self, mock_set_fh, mock_time, mock_makedirs):
        """
        Check if only the two default handlers are set even if the class
        is initiated repeatedly.
        """
        mock_time.now.return_value = self.exec_time
        mkdir_calls = [
            mock.call(os.path.join(
                self.outputdir, submod11.LOGDIR),
                exist_ok=True)]

        for i in range(3):
            sc = submod11.SampleClass(self.loglevel, self.outputdir)
            mock_makedirs.assert_has_calls(mkdir_calls)
            mock_set_fh.assert_called_with(
                sc.logger.parent, self.logfilename,
                self.loglevel, submod11.HANDLERNAME_FILE)
            self.assertEqual(sc.logger.parent, self.parent_logger,
                             "parent logger is package logger")
            self.assertEqual(sc.logger.parent.name, logging_sandbox.__name__,
                             "Names of SampleClass parent logger and package "
                             + "are equal")
            self.assertTrue(len(sc.logger.parent.handlers) == 1,
                            "parent logger has 2 handlers")
            self.assertTrue(len(sc.logger.handlers) == 0,
                            "Class loggers has no handlers")


if __name__ == "__main__":
    main()
