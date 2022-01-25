#########################################
#					#
#	Multi-Connection Web Server	#
#					#
#########################################

# Imports
from socket import *
from os.path import exists as file_exists
import re
import sys
import select
import queue

# Globals 
ERROR_HTML_404 = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">\r\n<html><head>\r\n<title>403 Forbidden</title>\r\n</head><body><h1>Access Refused</h1>\r\n<p>The requested URL was forbidden on this server.</p>\r\n</body></html>'''
ERROR_HTML_403 = '''<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">\r\n<html><head>\r\n<title>404 Not Found</title>\r\n</head><body><h1>Not Found</h1>\r\n<p>The requested URL was forbidden on this server.</p>\r\n</body></html>'''

# Funcs
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
	print(tokenized_req)
	# Get HTTP Action Line tokens
	action_line_toks = tokenized_req[0].split()
	# Get Verb, HTTP Version, Filename
	http_verb, http_ver, req_file = action_line_toks[0], action_line_toks[2], action_line_toks[1]
	req_file = req_file.replace("/", "")
	print(f"HTTP VERB: {http_verb}\n HTTP VER: {http_ver}\n REQ FILE: {req_file}")
	# Retern Parsed req
	return http_verb, http_ver, req_file

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
	# Set options for testing
	servSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
	# Set Blocking to False
	servSocket.setblocking(0)
	
	# Attempt to bind socket
	try:
		# Bind
		servSocket.bind(("", servPort))
		# Listen for conn(s)
		servSocket.listen(5)

	# Get error exception
	except error:
		# Print Error
		print(error)

	# Containers for input/output sockets
	out_sockets = []
	in_sockets = [servSocket]

	# Server Loop
	while in_sockets:
		# Call Select and get read_list, write_list, and execp_list
		read_list, write_list, excep_list = select.select(in_sockets, out_sockets, in_sockets)
		# Get socket from read_list
		for conn in read_list:
			print(f"The socket is: {conn}\n")
			print(f"The list of out_sockets is: {out_sockets}")
			print(f"The list of in_sockets is: {in_sockets}")
			# Check if servSocket
			if conn is servSocket:
				# Ready to accept another conn
				connSocket, addr = conn.accept()	
				# Test Print
				print(f"Connection from {connSocket}:{addr}")
				connSocket.setblocking(1)
				# Add socket to inputs
				in_sockets.append(connSocket)
		
			# Otherwise, check for data
			else:
				# Attempt to read HTTP req
				req = conn.recv(2048).decode()
				# Check data exists
				if req:
					http_verb, http_ver, req_file = parseHeaderContent(req)	
					# Check file exists
					if checkExists(req_file):
						if isHTML(req_file):
							print("Constructing 200 OK")
							# Send 200 OK msg
							http_msg = makeResponse(req_file, '200 OK')
							print("Sending 200 OK Message")
							# Send 200 OK Msg
							conn.send(http_msg)
							in_sockets.remove(conn)
							conn.close()
							
						else:
							print("Constructing 403 Forbidden")	
							# SEND 403 Forbidden Msg
							http_msg = makeResponse(req_file, '403 Forbidden')
							print("Sending 403 Forbidden")
							# Send 403 msg
							conn.send(http_msg)
							in_sockets.remove(conn)
							conn.close()
					else:
						print("Constructing 404 Not Found")
						# Send 404 Not Found msg
						http_msg = makeResponse(req_file, '404 Not Found')
						# Send 404 msg
						print("Sending 404 Not Found")
						conn.send(http_msg)
						in_sockets.remove(conn)
						conn.close()
						

				# 	# Check if in output list	
				# 	if s not in out_sockets:
				# 		# If not, Append to output list
				# 		out_sockets.append(s)
				# else:
				# 	# Test Print
				# 	print(f"Closing: {addr}")
				# 	# No data, ready to disconnect
				# 	if s in out_sockets:
				# 		# Remove from outputs
				# 		out_sockets.remove(s)
				# 	# Remove from inputs
				# 	in_sockets.remove(s)
				# 	# Close
				# 	s.close()

if __name__ == '__main__':
	# Get Port come cmdline
	port = int(sys.argv[1])
	# Run main with port
	main(port)