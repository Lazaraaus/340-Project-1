import socket
import sys

redirect_num = 0

def http_client(url):
    #check for redirects
    global redirect_num
    redirect_num += 1
    if redirect_num == 10:
        print('Too Many Redirects', file = sys.stderr)
        sys.exit(1)

    #get host and port

    #check if url given is valid
    if url[:5] == 'https':
        print('HTTPS is not accepted in the url', file = sys.stderr)
        sys.exit(1)
    if url[0:7] != 'http://':
        print('URL must start with http://', file = sys.stderr)
        sys.exit(1)


    #Get rid of http:// to get host
    port = 80
    host = url[7:]
    
    #if port is specified in url
    if host.find(":")!=-1:
        port_str = host[host.find(':')+1:]
        if port_str.find('/') != -1:
            port_str = port_str.replace('/', ' ')
        port = int(port_str)
        host = host[:host.find(":")]

    if host.find('/') != -1:
        index = host.find('/')
        if len(host[index:]) == 1:
            path = '//'
        else:
            path = "//" + host[index+1:]
        host = host[:index]
    else:
        path = '//'
        

    #code based on https://realpython.com/python-sockets/#application-client-and-server and https://www.geeks3d.com/hacklab/20190114/python-3-stoppable-tcp-server-and-tcp-client-with-geexlab/
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    client.connect( (host, port) )
    req_header = 'GET /%s HTTP/1.0\r\nHost: %s\r\n\r\n' % (path, host)
    req_header = req_header.encode()
    client.sendall(req_header)

    #receiving data, code based on https://iximiuz.com/en/posts/writing-web-server-in-python-sockets/ and https://stackoverflow.com/questions/47658584/implementing-http-client-with-sockets-without-http-libraries-with-python
    data = []
    response = client.recv(4096)
    data.append(response)
    while True:
        data_part = client.recv(4096)
        if not data_part:
            break
        data.append(data_part)

    for i in range(len(data)):
        data[i] = data[i].decode('latin-1')
    response = ''.join(data)
    response = response[9:]
    response = response.split('\r\n')

    
    status = response[0][:3]
    response_len = len(response)

    if status == "200":
        for i in range(response_len):
            if response[i].find('Content-Type: text/html') != -1:
                print(response[response_len - 1])
                sys.exit(0)
        sys.exit(1)

    elif status == "301" or status == "302":
        for i in range(response_len):
            if response[i].find('Location') != -1:
                redir_location = response[i][10:]
        print("Redirected to:  " + redir_location, file = sys.stderr)
        http_client(redir_location)

    elif status >= "400":
        for i in range(response_len):
            if response[i].find('Content-Type: text/html') != -1:
                print(response[response_len-1])
        sys.exit(1)

if __name__ == '__main__':
    http_client(sys.argv[1])