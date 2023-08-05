#!/usr/bin/env python

import sys
import optparse

def get_option_parser():
    usage = "%prog <config file> <application id> [options]"
    op = optparse.OptionParser(usage=usage)
    op.add_option("-u", "--update",
    action="store_true", dest="update", default=False,
    help="Update dependencies and other egg info using `sudo python setup.py develop` before running (setup.py must be in cwd, user must have sudo permission)")
    op.add_option("-i", "--interact",
    action="store_true", dest="interact", default=False,
    help="Open up an interactive prompt with the correct environment.")
    op.add_option("-n", "--num", type="int", dest="num", default=1,
    help="Use config substitution, swapping $num for given value.")
    op.add_option("--spawn", action="store",
    help="Used internally when spawning processes.")
    return op

def run():
    parser = get_option_parser()

    prog_args = []
    monster_args = sys.argv
    if '!' in sys.argv:
        delimiter_index = sys.argv.index('!')
        prog_args = sys.argv[delimiter_index+1:]
        monster_args = sys.argv[:delimiter_index]

    options, args = parser.parse_args(monster_args[1:])
    if len(args) != 2:
        parser.error("monster_run requires exactly two arguments: config file and application id")

    from eggmonster import runner

    runner.main(*args + [options.update, options.interact, options.num, options.spawn, prog_args])
