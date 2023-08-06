#!/usr/bin/python

import yospaceCDS
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

print "Live:-"
print yospaceCDS._ContentClient

#yospaceCDS.buildConnections("cds1.stg.yospace.com")
#
#print "Staging:-"
#print yospaceCDS._ContentClient

