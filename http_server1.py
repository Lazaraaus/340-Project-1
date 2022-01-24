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

# Globals 
ERROR_HTML_404 = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">\r\n<html><head>\r\n<title>403 Forbidden</title>\r\n</head><body><h1>Access Refused</h1>\r\n<p>The requested URL was forbidden on this server.</p>\r\n</body></html>'''
ERROR_HTML_403 = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">\r\n<html><head>\r\n<title>404 Not Found</title>\r\n</head><body><h1>Not Found</h1>\r\n<p>The requested URL was forbidden on this server.</p>\r\n</body></html>'''


def isHTML(file):
	"""
	Func to check if a file is an .htm or .html
	"""	
	is_html = ".html" in file or ".html" in file
	return is_html

def parseHeaderContent(req):
	"""
	Func to parse Header Content in GET req.	
	I think this should work (regex101). Should match the GET verb and the pull the file
	req'd into the 1st capture group.

	Alternatively, you can just tokenize the req using splits on newline and space respectively.

	I believe the regex is faster though
	"""
	# Tokenize the req
	tokenized_req = req.split("\n")
	# Get HTTP Action Line tokens
	action_line_toks = tokenized_req[0].split()
	# Get Verb, HTTP Version, Filename
	http_verb, http_ver, req_file = action_line_toks[0], action_line_toks[2], action_line_toks[1]
	req_file = req_file.replace("/", "")

	# Compile Pattern
	pattern = re.compile('GET\s/(.*?)\s')
	# Parse Header w/ Pattern
	parsed_req = re.findall(pattern, req)
	# Retern Parsed req
	return parsed_req, http_verb, http_ver, req_file

def makeResponse(file, status):
	"""
	Func to construct an HTTP Response for a client's HTTP Request.
	Needs to construct Header and attach file contents to the body of the HTTP msg
	"""
	global ERROR_HTML_403, ERROR_HTML_404
	# Header will always have these attribs
	header = "HTTP/1.1 " + status + "\r\nContent-Type: text/html\r\n\r\n"
	print(header)
	# Check for status
	if status == '200 OK':
		with open(file, 'r') as f:
			# Get contents of files
			header += f.read()
			f.close()
		# Return Header
		return header.encode()
	# Check for 404
	elif status == '404 Not Found':
		# Get 404 error HTML
		error_html = ERROR_HTML_404
		# Add to header
		header += error_html
		# Return header
		return header.encode()
	# Check for 403
	elif status == '403 Forbidden':
		# 403 error HTML
		error_html = ERROR_HTML_403 
		# Add to header
		header += error_html
		# Return header
		return header.encode()

def checkExists(file):
	"""
	Func to check if the file requested by the client exists in the directory
	"""
	# Return file_exists(file)
	exists = file_exists(file)
	return exists

def main(port):
	"""
	Func to hold the server logic/loop
	"""
	# Create Welcome Socket
	servPort = port
	servSocket = socket(AF_INET, SOCK_STREAM)
	
	# Attempt to bind socket
	try:
		# Bind
		servSocket.bind(("", servPort))
		# Listen for conn(s)
		servSocket.listen(1)

	# Get error exception
	except error:
		# Print Error
		print(error)

	# Server Loop
	while True:
		# Accept conn
		connSocket, addr = servSocket.accept()
		# Get 1024 Bytes from the socket
		req = connSocket.recv(1024).decode()

		# Parse the Req
		# Print the req
		print(req)
		tokenized_req = req.split("\n")
		print(f"\nThe tokenized req is: {tokenized_req}")
		parsed_req, http_verb, http_ver, req_file = parseHeaderContent(req)
		print(f"\nThe parsed req is: {parsed_req}")
		print(f"\nThe HTTP Verb: {http_verb}\nThe HTTP Ver: {http_ver}\nThe Requested File: {req_file}")
		exists = checkExists(req_file)
		print(exists)

		# Check if file exists on server
		if checkExists(req_file):
			# Check if HTML/HTM
			if isHTML(req_file):
				# Construct 200 OK Message
				http_msg = makeResponse(req_file, '200 OK')
				# Send 200 OK Message
				connSocket.send(http_msg)
				
			# Otherwise
			else:
				# Construct 403 Forbidden Message
				http_msg = makeResponse('', '403 Forbidden')
				# Send 403 Forbidden Message
				connSocket.send(http_msg)
			
		# Otherwise
		else:
			# Construct 404 Not Found Message
			http_msg = makeResponse('', '404 Not Found')
			# Send 403 Forbidden Message
			connSocket.send(http_msg)

		# Close Socket
		connSocket.close()

if __name__ == '__main__':
	# Get Port come cmdline
	port = int(sys.argv[1])
	# Run main with port
	main(port)