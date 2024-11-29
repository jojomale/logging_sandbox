import logging
from .. import logfactory


parentlogger = logfactory.create_logger()
module_logger = logging.getLogger(parentlogger.name+".submod21")


class ClassInOtherModule():
    def __init__(self):
        self.logger = logging.getLogger(module_logger.name
                                        + ".ClassInOtherModule")
        self.logger.debug("Instance created.")

    def do_stuff(self):
        self.logger.info("Doing stuff")
        some_func_in_other_mod()


def some_func_in_other_mod():
    # print("Name of submod21 logger", module_logger.parent.name)
    module_logger.debug("Executing debug log")
    module_logger.warning("Executing warning log")
