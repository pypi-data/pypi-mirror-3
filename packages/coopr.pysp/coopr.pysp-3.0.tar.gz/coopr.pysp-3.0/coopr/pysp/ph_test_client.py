#! /usr/bin/env python

import Pyro.core
import Pyro.naming

import pickle

import pyutilib.misc
import pyutilib.component.core
from coopr.opt.results import SolverResults

import sys

def main():
    if len(sys.argv) != 2:
        print "***Incorrect invocation - use: ph_client scenario-name"
        sys.exit(0)

    scenario_name = sys.argv[1]

    print "STARTING"

    Pyro.core.initClient(banner=1)

    print "ATTEMPTING TO LOCATE NAME SERVER"
    locator = Pyro.naming.NameServerLocator()
    ns = locator.getNS()
    print "FOUND NAME SERVER"

    uri = None
    try:
        uri = ns.resolve(scenario_name)
    except Pyro.errors.NamingError:
        print "***ERROR: Failed to locate server capable of processing scenario="+scenario_name
        sys.exit(0)

    print "URI=",uri

    print "CREATING PROXY OBJECT"

    obj = Pyro.core.getProxyForURI(uri)

    print "CALLING SOLVE METHOD"
    encoded_result = obj.solve(scenario_name)
    result = pickle.loads(encoded_result)
    print "SUCCESSFULLY OBTAINED RESULT!"

    print "RESULTS:"
    result.write(num=1)

    print "DONE"

if __name__ == '__main__':
    main()
