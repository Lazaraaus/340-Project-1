#########################################
#					#
#	Multi-Connection Web Server	#
#					#
#########################################


from socket import *
from os.path import exists as file_exists
import re
import sys

def isHTML(file):
	"""
	Func to check if a file is an .htm or .html
	"""	
	pass

def makeResponse(body, file, status):
	"""
	Func to construct an HTTP Response for a client's HTTP Request
	"""
	pass

def checkExists(file):
	"""
	Func to check if the file requested by the client exists in the directory
	"""
	pass

def main(port):
	"""
	Func to hold the server logic/loop
	"""

	pass


if __name__ == '__main__':
	# Get Port come cmdline
	port = int(sys.argv[1])
	# Run main with port
	main(port)