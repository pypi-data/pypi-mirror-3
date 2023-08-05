# Create a test runner script, but include modules modules in addition
#  to py.test
from _pytest import genscript
script = genscript.generate_script(
	entry = 'import py; raise SystemExit(py.test.cmdline.main())',
	packages = ['py', '_pytest', 'pytest', 'dingus'],
)
with open('run-tests.py', 'wb') as script_file:
	script_file.write(script)
