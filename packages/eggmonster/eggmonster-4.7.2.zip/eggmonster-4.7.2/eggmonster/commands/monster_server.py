#!/usr/bin/env python

import sys, os
from optparse import OptionParser

from eggmonster.server import main

def setup_parser():
    parser = OptionParser()
    parser.add_option("-p", "--port", dest="port", type=int,
                                    help="listen on port PORT (default 8000)", metavar="PORT")
    parser.add_option("-a", "--authdb", dest="passwd", type=str,
                                    help="path to file with Basic Auth password hashes (default no auth)",
                                    metavar="PASSWD")

    parser.set_defaults(port=8000, passwd='')

    return parser

def run():
    parser = setup_parser()

    options, args = parser.parse_args()
    if len(args) != 1:
        parser.error("monster_server requires exactly one argument: config_directory")

    config_directory = args[0]

    if not os.path.isdir(config_directory):
        parser.error("the given path is not a directory")

    main(config_directory, options.port, options.passwd)
