# Sample project on logging

This project was an exercise for a real project for which I wanted to
introduce logging.

# How to use
Install package using `pip`. Use editable mode (`-e` flag) if you want to 
play around. From package directory, do:
    ```
    pip install -e .
    ```

## Software prerequisites
- python >= 3.9 (lower versions might work)
- mpi4py


Then  execute `scripts/run.py`. 
Without parallelization:
    ```
    python scripts/run.py
    ```
With parallelization:
    ```
    mpirun -n 2 python scripts/run.py
    ```
`-n` sets the number of cores to use. Using `-n 1` basically 
deactivates parallelization.
When executed, a subdirectory `output/log` should be created,
including N log-files, N corresponding to the number of cores
you chose.

The `run.py`-script mimics the user access to the package.
Play around with the `loglevel`, to see its influence.

You can, of course, also change things in the package itself
(everything in `src`) and watch the changes when running the 
script.



# Logging set up
## Logging requirements
I had several requirements for the logging:
- log messages, i.e. loggers should know and express from where they are
  executed, i.e. know package, module, class, function which called them.
- The main functionality of the package is provided by the execution method
  of two distinct classes (for the sample here I used only 1). They are 
  typically called in a short script.
- These main classes call functions from several modules, their own methods,
  and have other helper classes as attributes which may also be called. Hence,
  tracing the origin of the log msg is important for debugging.
- the package is parallelized using `mpi4py`
- the package is typically executed on a computation cluster
- as part of the functionality, the main class provides a standard logging 
  procedure, the level of which is an init argument
- standard logging should go to console and to log files 
  --> two handlers required
- Log files & MPI: Since multiple processes can not write to the same file,
  each process has to create its own log file
- Ideally the user can add their own handlers to the base logger
- avoid accumulation of default handlers in main class if instantiated
  repeatedly

In order to achieve this, I replicated the project using a simplified structure
and focusing on the logging.

## Key apects
- have a module `logfactory`
	- -> function to create basic logger
	- provide fmt for handlers
- in each module, initiate a `module_logger` using 
	```
	logger = logfactory.create_logger()
	module_logger = logging.getLogger(logger.name+".submod11")
	```
- in (main) classes like the `Corelator` we can add a child of the module-logger as attribute
	- if we want to control the loglevel of all loggers from the parameters given to the class, we need to set loglevels, handlers, etc. to the parent logger, e.g.:
	```
	self.logger = logging.getLogger(module_logger.name+"..Correlator")
	self.logger.parent.setLevel(loglvl)
	```
	- for some reason, if set as attribute, the correct parent logger is not found if you use the intuitive naming pattern 
		- Suppose `module_logger = logging.getLogger(parentlogger.name+".submod11")` 
		- thus `module_logger.name` is `parent.submod11`
		- Intuitively I wanted to use `self.logger = logging.getLogger(module_logger.name+".Correlator")` in the class init
		- However then the parent logger of `self.logger` becomes `parent.submod11` instead of `parent` like I intended.
		- It can be solved using e.g. `self.logger = logging.getLogger(module_logger.name+"..Correlator")`
		- **WHYYYYYYY!?!?!?!?!?!?**
