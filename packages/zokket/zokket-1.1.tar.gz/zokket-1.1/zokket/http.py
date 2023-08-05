class HTTPSocketDelegate(object):
    def request_did_timeout(self, request):
        pass

    def request_complete(self, request, response):
        pass

    def request_failed(self, request):
        pass

class HTTPRequest(object):
    @classmethod
    def url(self, url):
        pass

    def __init__(self, host, port=80, ssl=False, path='/', method='GET', headers={}):
        self.headers = headers
        self.method = method

        self.host = host
        self.port = port
        self.ssl = ssl

        self.path = path

    def write_to_sock(self, sock):
        sock.write("{} {} HTTP/1.0\r\n".format(self.method, self.path))

        #if self.data:
        #    data_string = urlencode(self.data)
        #    self.headers['Conent-Length'] = len(data_string)

        for k,v in self.headers.items():
            sock.write("{}: {}\r\n".format(k, v))

        sock.write("\r\n")

        #if data:
        #    sock.write("{}\r\n".format(data_string)

    def socket_read_data(self, sock, data):
        pass

class HTTPResponse(object):
    def __init__(self, status_code, content='', headers={}):
        self.status_code = status_code
        self.content = content
        self.headers = headers

    def is_redirect(self):
        return (self.status_code == 301 or self.status_code == 302) and 'Location' in self.headers

    def __str__(self):
        return self.content

    def __repr__(self):
        return '<HttpResponse {} ({})>'.format(self.status_code, self.headers)


