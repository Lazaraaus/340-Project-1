#################################
#	Simple HTTP Server 	# 
#################################


# Goal: Write an HTTP Server that handles one connection and serves any files that end in .html or .htm
# Should have cmd line interface: python3 http_server.py [port]


# Create a welcoming TCP socket
# Bind that socket to the [port] given by the user
# Listen for TCP connections
# Do the following:
	# Accept new connection on the socket		func: main()
	# Read the HTTP request		func: Strip file name from HTTP Get Header
	# See if the file exists	func: checkExists()
	# If so, construct HTTP response. Write and send header, then open the file and write its contents to the conn socket 	func: makeResponse()
	# If not, construct the proper HTTP response (404 Not Found) or (403 Forbidden) 					func: makeResponse()
	# Close the socket

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