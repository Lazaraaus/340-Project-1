# Imports
from socket import *
from os.path import exists as file_exists
import re
import sys
import json
import math

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
	# Example Query: GET /product?a=12&b=60&another=0.5
	# Tokenize the req
	tokenized_req = req.split("\n")
	# Get HTTP Action Line tokens
	action_line_toks = tokenized_req[0]
	# Split on &
	action_line_toks = action_line_toks.split("&")
	print(f"Action Line Tokens: {action_line_toks}\n")
	req_first_arg_toks = action_line_toks[0].split(" ")
	req_first_arg_toks = req_first_arg_toks[1].split("?")
	req_endpoint = req_first_arg_toks[0]
	print(f"The request endpoint is: {req_endpoint}\n")
	first_arg = req_first_arg_toks[1].split("=")[1]
	second_arg = action_line_toks[1].split("=")[1]
	third_arg = action_line_toks[2].split(" ")[0].split("=")[1]	
	print(action_line_toks[2])
	print(f"The first arg: {first_arg}\nThe second arg: {second_arg}\nThe third arg: {third_arg}\n")

	# Retern Parsed req
	return req_endpoint, first_arg, second_arg, third_arg

def makeResponse(arg1, arg2, arg3, status, all_floats=True):
	"""
	Func to construct an HTTP Response for a client's HTTP Request.
	Needs to construct Header and attach file contents to the body of the HTTP msg
	"""
	global ERROR_HTML_403, ERROR_HTML_404
	# Header will always have these attribs
	header = "HTTP/1.1 " + status + "\r\nContent-Type: application/json\r\n\r\n"
	print(header)
	# Check for status
	if status == '200 OK':
		if all_floats:
			# Calc Product
			product = float(arg1) * float(arg2) * float(arg3)
			# Check for inf
			if math.isinf(product):
				# If so, make str "inf"
				product = "inf"
			# Build resp dict
			resp = {
				"operation": "product",
				"operands": [float(arg1), float(arg2), float(arg3)],
				"result": product
			}
			# Dump to JSON
			resp = json.dumps(resp)
			# Append to header
			header += resp
			# Return Header
			return header.encode()
		else:
			try:
				product = float(arg1) * float(arg2)
				arg2 = float(arg2)
				arg1 = float(arg1)
			except:
				product = float(arg1)	
				arg1 = float(arg1)
			if math.isinf(product):
				product = "inf"
			resp = {
				"operation": "product",
				"operands": [arg1, arg2, arg3],
				"result": product
			}
			resp = json.dumps(resp)
			header += resp
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

def checkGoodInputs(args):
	# Check if all args exist
	if all(args):
		# Loop through args
		for arg in args:
			# Try
			try:
				# Cast arg to float
				flt_arg = float(arg)
			except:
				# If not, return false
				return False
		# Otherwise, return True	
		return True

def checkOneGoodInput(args):
	# Check for at least one non-empty input
	good_inputs = []
	if any(args):
		# Var to hold return val
		return_val = ''
		# Loop through args
		for idx, arg in enumerate(args):
			try:
				# Try to cast to float
				flt_arg = float(arg)
				# If so, set as return_val
				return_val = flt_arg
				# If so, append to good_inputs
				good_inputs.append(str(int(flt_arg)))
			except:
				# Check if end of arg list
				if idx == len(args):
					# If so, return False and empty return_val
					return (False, '')
		# Return True, return_val
		return (True, good_inputs)

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
		req_endpoint, first_arg, second_arg, third_arg = parseHeaderContent(req)

		# Check if file exists on server
		if req_endpoint == '/product':
			# Check All Good Inputs
			if checkGoodInputs([first_arg, second_arg, third_arg]):
				# Construct 200 OK Message
				http_msg = makeResponse(first_arg, second_arg, third_arg, '200 OK')
				# Send 200 OK Message
				connSocket.send(http_msg)
			
			elif checkOneGoodInput([first_arg, second_arg, third_arg])[0]:	
				args = [first_arg, second_arg, third_arg]
				# Get good values from query params
				good_vals = checkOneGoodInput(args)[1]
				print(good_vals)	
				# Loop through good_vals and remove each val from args
				for val in good_vals:
					args.remove(val)
				print(args)
				# Check if more good_vals or bad_args
				if len(args) > len(good_vals):
					http_msg = makeResponse(good_vals[0], args[0], args[1], '200 OK', all_floats=False)
				else:
					http_msg = makeResponse(good_vals[0], good_vals[1], args[0], '200 OK', all_floats=False)
				connSocket.send(http_msg)
			# Otherwise
			else:
				# Construct 403 Forbidden Message
				http_msg = makeResponse('', '', '', '403 Forbidden')
				# Send 403 Forbidden Message
				connSocket.send(http_msg)
			
		# Otherwise
		else:
			# Construct 404 Not Found Message
			http_msg = makeResponse('', '', '', '404 Not Found')
			# Send 403 Forbidden Message
			connSocket.send(http_msg)

		# Close Socket
		connSocket.close()

if __name__ == '__main__':
	# Get Port come cmdline
	port = int(sys.argv[1])
	# Run main with port
	main(port)