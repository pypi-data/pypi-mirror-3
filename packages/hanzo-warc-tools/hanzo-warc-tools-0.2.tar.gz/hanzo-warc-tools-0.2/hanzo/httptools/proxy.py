from .messaging import RequestParser, ResponseParser

class ProxySession(object):
    def __init__(self, client):
        self.request_parser = RequestParser()
        self.response_parser = ResponseParser()


    def run(self):
        # read from client, 
        # canonicalize request
        # forward header if there

        # read replies from server
        # forward responses

        # close or re-use connection
