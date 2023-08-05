#!/usr/bin/env python
'''
Created on Nov 25, 2011

@author: Joseph Piron
'''
from jsonrpclib import Server
from pprint import pprint
import optparse
import sys


parser = optparse.OptionParser("%prog <rpccmd1> <rpccmd2> ..")
parser.add_option('-s', action = "store", dest = "host", default = "localhost",
                  help = "server to connect to")
parser.add_option('-p', action = "store", dest = "port", default = "8080",
                  help = "port used by the server")
parser.add_option('-u', action = "store", dest = "url", default = "",
                  help = "relative url of the rpc service (ex: 'jsonrpc/api')")

(options, args) = parser.parse_args(sys.argv)

if len(args) > 1:
    proxy = Server("http://%s:%s/%s" % (options.host, options.port, options.url))
    for cmd in args[1:]:
        print("Running %s:" % cmd)
        try:
            pprint(getattr(proxy, cmd)())
        except Exception, E:
            print E.message
else:
    parser.print_usage()
