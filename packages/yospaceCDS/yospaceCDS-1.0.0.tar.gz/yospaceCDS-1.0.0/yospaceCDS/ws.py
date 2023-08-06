#!/usr/bin/python

import suds.client

# Which Yospace CDS platform should be targetted?
CDSDOMAIN = "cds1.yospace.com"

#-- "Abstract" WebService Client Class ----------------------------------------

class _ws(suds.client.Client):
	"Convenience class for CDS Web Services, based on the WSDL"

	SERVICEADDRESS = "set_this_to_a_service_address"

	def __init__(self, service=None, faults=True):
		"Connect to the service and remember the un/pw"
		# Set the service address
		if service:
			self.SERVICEADDRESS = service
		# Initialise the SOAP sub-system, including loading the WSDL
		suds.client.Client.__init__(
			self,
			self.SERVICEADDRESS,
			faults=faults,
		)

#-- Content Service -----------------------------------------------------------

class ContentService(_ws):
	"CDS ContentService Client"
	def __init__(self, service=None, faults=True):
		self.SERVICEADDRESS = "https://%s/cds-controller/contentService?wsdl" % (CDSDOMAIN, )
		_ws.__init__(
			self,
			service=service,
			faults=faults,
		)

#-- Media Item Service --------------------------------------------------------

class MediaItemService(_ws):
	"CDS ContentService Client"
	def __init__(self, service=None, faults=True):
		self.SERVICEADDRESS = "https://%s/mediaitemmanager/manage?wsdl" % (CDSDOMAIN, )
		_ws.__init__(
			self,
			service=service,
			faults=faults,
		)

if __name__ == '__main__':
# Simple testing
	cs = ContentService()
	print cs

	mis = MediaItemService()
	print mis
