#!/usr/bin/python

import yospaceCDS
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)

yospaceCDS.buildConnections("cds1.yospace.com")

print yospaceCDS._MediaItemClient

#print yospaceCDS.CreateMediaItem("yospace01", "myflow", "http://qa.broadcastcdn.reuters.com/testdata/T999-UK-Test.mpg", 12210221, True, True, 'video/mpg', 'Regression Test Video', 'Regresion test video for the media item API', '', 1289819499.0)
print yospaceCDS.GetMediaItems("yospace01", "myflow", 12210221)
#print yospaceCDS.deleteMediaItem("yospace01", "myflow", 12210221)
#print yospaceCDS.StatusMediaItem("yospace01", "myflow", 12210312)
