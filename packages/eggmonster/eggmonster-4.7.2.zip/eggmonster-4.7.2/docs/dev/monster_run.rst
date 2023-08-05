^^^^^^^^^^^
monster_run
^^^^^^^^^^^

Usage: ``monster_run [options] <config.yaml> <entry_point>``

Arguments
~~~~~~~~~

config.yaml:
	the path to the configuration file

entry_point:
	the function to run


Options
~~~~~~~

-u/--update:
	Update dependencies and other egg info using `sudo python setup.py develop`
	before running (setup.py must be in cwd, user must have sudo permission)
	
-i/--interact:
	action="store_true", dest="interact", default=False,
	help="Open up an interactive prompt with the correct environment.")

-n/--num:
	Use config substitution, swapping $num for given value.

--spawn:
	Used internally when spawning processes.


Discussion
~~~~~~~~~~





