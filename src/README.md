# For swsuite installers and developers

This documentation is for the different files in the slurm wrapper.
Let's start with an overview of all the files and how they are connected.

## swconf.yaml
Contains values such as defaults, limits, environment variable names (preceded by $) and lists.
Purpose is to change certain values such as default shell from /bin/bash to /bin/zsh or change the default allowed partitions from ['cpu', 'gpux1'] to ['cpu', 'gpux1', 'gpux2']
The environment variable mechanism works because swtools.py parses it and interprets it as such.

## swtools.py
The main work is done here.

Operated in 2 ways:
1) Imported as
```python
from swtools import builder
```
2) Run as 
```bash
python swtools.py [-h] [-l]
```
* log (_optional_) : Create a local text file to log all the tests

	You can the cat the test file to see the colorized output of pass/fail and all the tests run with their respective outputs.

##### Layout of the script
1) It includes a class called Builder.
2) It pulls values from a yaml conf file defined at the beginning and converts them into global variables to use in the script (this is done in the \_\_init\_\_ method).
3) Main data object is job_parameters (which is a dictionary).
4) The build_command and build_script both call an internal build function which operated on the job parameters dictionary, cleanup values and then do their own work after that.

##### To add a new parameter
1) Create a check function like the ones defined already
2) Convert the function into a callable object using partial
3) Add the object to the rules dictionary in the \_\_init\_\_ method with the appropriate name (which is the name of the parameter usually)
4) Mention the new parameter as either a user enter parameter or not in the respective swrun.py/ swbatch.py scripts.

## swrun.py and swbatch.py
Main functionality is parsing the arguments and creating a builder object with the arguments to: generate a 
- generate a runnable slurm command, _or_
- convert a simplified batch script to an appropriate one

The swbatch additionally currently has support for logging these batch scripts(for analysis purposes) under a hidden user directory in read-only mode but it is recommended to configure slurm to do so itself.

>**NOTE**: The scripts set traceback limit to 0 to essentially suppress it for the user's convenience. Hidden flag [-d] can be included to disable the traceback supression. This is for debugging purposes.
