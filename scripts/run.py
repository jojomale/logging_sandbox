from logging_sandbox.module1.submod11 import SampleClass
from logging_sandbox import logfactory
import logging
import os
from mpi4py import MPI


# init MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()


# Set up logger for script using package logger
parentlogger = logfactory.create_logger()
logger = logging.getLogger(parentlogger.name + ".script")
logger.setLevel("DEBUG")
logfactory.set_consoleHandler(logger, "DEBUG")

# Delete old logfiles
if rank == 0:
    logdir = os.path.join("output", "log")
    if os.path.isdir(logdir):
        for f in os.listdir(logdir):
            os.remove(os.path.join(logdir, f))
comm.Barrier()

# Init SampleClass and run methods several times
for i in range(3):
    logger.info("Starting run %d" % i)
    logger.info("My parent is %s" % logger.parent.name)
    sc = SampleClass("DEBUG", "output")
    sc.do_something()
    sc.do_something_different()
    sc.do_something_with_other_class()
    logger.info("\n")
