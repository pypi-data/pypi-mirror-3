# -*- coding: utf-8 -*-

import sys
import Seraph
import argparse

if __name__ == '__main__':
    p = argparse.ArgumentParser(\
            description="Seraph, a static blog generator.",
            prog="Seraph")
    p.add_argument("-l","--local",action='store_true',\
            help="Enable local mode for testing")
    p.add_argument("--push",action='store_true',\
            help="Push the built site to your git repo")
    p.add_argument("--init",action='store_true',\
            help="Init a site in specific directory.")
    p.add_argument("-b", "--build",action="store_true",
            help="Build a site.")
    args = p.parse_known_args()
    if args[0].local or args[0].build:
        site = Seraph.Site(args[0].local)
        site.build()
    elif args[0].push:
        Seraph.extra.git_push()
    elif args[0].init:
        loc = "site/"
        if args[1]:
            loc = args[1][0]
        Seraph.extra.init_site(loc)
    else:
        p.print_help()
