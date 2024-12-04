from unittest import TestCase, main, mock
import os
import shutil
import logging
from logging_sandbox import logfactory
from logging_sandbox.module1 import submod11
import logging_sandbox
from datetime import datetime


# class TestSampleClass(TestCase):
#     def setUp(self) -> None:
#         self.outputdir = "output"
#         self.parent_logger = logfactory.create_logger()
#         self.exec_time = datetime(2021, 1, 1, 0, 0, 0)
#         self.logfilename = os.path.join(
#             self.outputdir, submod11.LOGDIR,
#             ('correlate%srank' + submod11.RANK_STRFMT) % (
#              self.exec_time.strftime(submod11.LOG_TSTRFMT), 0))
#         self.loglevel = "CRITICAL"
#         return super().setUp()

#     def tearDown(self) -> None:
#         if os.path.isdir(self.outputdir):
#             shutil.rmtree(self.outputdir)
#         return super().tearDown()

#     @mock.patch("logging_sandbox.module1.submod11.datetime")
#     def test_logfile_creation(self, mock_time):
#         mock_time.now.return_value = self.exec_time
#         sc = submod11.SampleClass(self.loglevel, self.outputdir)
#         self.assertEqual(sc.logger.parent, self.parent_logger)
#         self.assertEqual(sc.logger.parent.name, logging_sandbox.__name__,
#                          "Name of parent logger of SampleClass is package name"
#                          )
#         self.assertTrue(os.path.isfile(self.logfilename),
#                         "Log file created")

#     @mock.patch("logging_sandbox.module1.submod11.os.makedirs")
#     @mock.patch("logging_sandbox.module1.submod11.datetime")
#     @mock.patch("logging_sandbox.module1.submod11.logfactory.set_fileHandler")
#     def test_handler_check(self, mock_set_fh, mock_time, mock_makedirs):
#         """
#         Check if only the two default handlers are set even if the class
#         is initiated repeatedly.
#         """
#         mock_time.now.return_value = self.exec_time
#         mkdir_calls = [
#             mock.call(os.path.join(
#                 self.outputdir, submod11.LOGDIR),
#                 exist_ok=True)]

#         for i in range(3):
#             sc = submod11.SampleClass(self.loglevel, self.outputdir)
#             mock_makedirs.assert_has_calls(mkdir_calls)
#             mock_set_fh.assert_called_with(
#                 sc.logger.parent, self.logfilename,
#                 self.loglevel, submod11.HANDLERNAME_FILE)
#             self.assertEqual(sc.logger.parent, self.parent_logger,
#                              "parent logger is package logger")
#             self.assertEqual(sc.logger.parent.name, logging_sandbox.__name__,
#                              "Names of SampleClass parent logger and package "
#                              + "are equal")
#             self.assertTrue(len(sc.logger.parent.handlers) == 1,
#                             "parent logger has 2 handlers")
#             self.assertTrue(len(sc.logger.handlers) == 0,
#                             "Class loggers has no handlers")


class TestSampleClass_Mock(TestCase):
    def setUp(self) -> None:
        self.outputdir = "output"
        self.exec_time = datetime(2021, 1, 1, 0, 0, 0)
        self.logfilename = os.path.join(
            self.outputdir, submod11.LOGDIR,
            ('correlate%srank' + submod11.RANK_STRFMT) % (
             self.exec_time.strftime(submod11.LOG_TSTRFMT), 0))
        self.loglevel = "CRITICAL"

        parent_logger = mock.create_autospec(logging.Logger)
        parent_logger.name = logging_sandbox.__name__
        self.parent_logger = parent_logger

        class_logger = mock.create_autospec(logging.Logger)
        class_logger.parent = parent_logger
        class_logger.name = (logging_sandbox.__name__
                             + ".submod11..SampleClass")

        sample_class = mock.create_autospec(submod11.SampleClass)
        sample_class.logger = class_logger
        sample_class.proj_dir = self.outputdir
        sample_class.rank = 0
        self.sample_class = sample_class

        return super().setUp()

    # def tearDown(self) -> None:
    #     if os.path.isdir(self.outputdir):
    #         shutil.rmtree(self.outputdir)
    #     return super().tearDown()

    @mock.patch("logging_sandbox.module1.submod11.logfactory.set_fileHandler")
    @mock.patch("logging_sandbox.module1.submod11.logfactory.set_consoleHandler")
    def test_set_logger(self, mock_set_ch, mock_set_fh):
        self.sample_class._set_logger(self.loglevel)
        mock_set_ch.assert_called_once_with(self.sample_class.logger, self.loglevel, submod11.HANDLERNAME_CONSOLE)
        mock_set_fh.assert_called_once_with(self.sample_class.logger, self.logfilename, self.loglevel, submod11.HANDLERNAME_FILE)
    
    # @mock.patch("logging_sandbox.module1.submod11.datetime")
    # @mock.patch("logging_sandbox.module1.submod11.os")
    # @mock.patch("logging_sandbox.module1.submod11.logfactory.set_fileHandler")
    # @mock.patch("logging_sandbox.module1.submod11.logfactory.set_consoleHandler")
    # def test_mk_logdir_get_logfilename(self, mock_set_ch, mock_set_fh, mock_os, mock_time):
    #     mock_time.now.return_value = self.exec_time

    #     self.sample_class._mk_logdir_get_logfilename()
    #     self.assertEqual(self.sample_class.rank, 0)
    #     mock_os.makedirs.assert_called_once_with(
    #         os.path.join(self.outputdir, submod11.LOGDIR), exist_ok=True)
    #     self.assertEqual(self.sample_class.logfilename, self.logfilename)

    # def test_default_handlers(self):
    #     pass

    # def test_set_logger(self):
    #     pass
    
    # @mock.patch("builtins.print")
    # def test_do_something(self, mock_print):
    #     sc = submod11.SampleClass("DEBUG", "output")
    #     sc.do_something()
    #     mock_print.assert_called_once_with("Hello")
    #     self.assertTrue(sc.logger.info.called)


if __name__ == "__main__":
    main()
