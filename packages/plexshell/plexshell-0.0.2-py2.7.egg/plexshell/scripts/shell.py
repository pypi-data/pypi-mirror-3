#!/usr/bin/env python
from plexshell import PlexShell
import argparse
import os


def main():
    parser = argparse.ArgumentParser(
        description = "A interactive command line PMS client")
    parser.add_argument(
        "-H", "--host",
        metavar = "hostname",
        nargs = "?",
        default = "localhost")
    parser.add_argument(
        "-p", "--port",
        metavar = "portno",
        nargs = "?",
        type = int,
        default = 32400)
    parser.add_argument(
        "-s", "--script",
        metavar = "scriptpath",
        nargs = "?",
        default = None)
    args = parser.parse_args()
    stdin = None
    if args.script:
        if not os.path.isfile(args.script):
            print "Script does not exist: %s" % args.script
            exit(1)
        stdin = open(args.script)
    client = PlexShell(args.host, args.port, stdin = stdin)
    client.cmdloop()


if __name__ == "__main__":
    main()
