from mpi4py import MPI
import logging
import os
from .. import logfactory
from ..module2 import submod21


parentlogger = logfactory.create_logger()
module_logger = logging.getLogger(parentlogger.name+".submod11")
LOGDIR = "log"


class SampleClass(logfactory.LoggingMPIBaseClass):
    def __init__(self, loglevel, proj_dir):
        # init MPI
        self.comm = MPI.COMM_WORLD
        self.psize = self.comm.Get_size()
        self.rank = self.comm.Get_rank()

        super().__init__()

        # directories
        self.proj_dir = proj_dir

        logdir = os.path.join(self.proj_dir, LOGDIR)
        self.set_logger(loglevel, logdir)
        self.other_class = submod21.ClassInOtherModule()

    def do_something(self):
        print("Hello")
        self.logger.info("I am doing something")

    def do_something_different(self):
        self.logger.info("Doing somethin' different")
        function_in_submod11()

    def do_something_with_other_class(self):
        self.other_class.do_stuff()


def function_in_submod11():
    module_logger.info("Info Hello")
    module_logger.debug("Debug Hello")
