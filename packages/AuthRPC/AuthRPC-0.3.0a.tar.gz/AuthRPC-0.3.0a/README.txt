This package provides a service based on JSONRPC with some small additions to the standard in order to enable authenticated requests.  The WSGI specification is used for data communication.  The package is broken down into two halves - a client and a server.  For security, the server is best run over HTTPS, although this is not enforced.

This package depends on WebOb 1.2 (or above).  This is automatically installed if you have an internet connection, otherwise download and install from http://pypi.python.org/pypi/WebOb

Example Usage (Server):

::

    import hashlib
    from wsgiref import simple_server
    from AuthRPC.server import AuthRPCApp

    def myauth(username, password, useragent):
        return username  == 'myuser' and \
               password  == hashlib.md5('secret'.encode()).hexdigest() and \
               useragent == 'myprogram'

    class api(object):
        def do_something(self, myvar):
            """Your code placed here"""
            return 'Something', myvar

    application = AuthRPCApp(api(), auth=myauth)
    simple_server.make_server('localhost', 1234, application)

Example Usage (Client):

::

    from AuthRPC.client import ServerProxy, BatchCall

    client = ServerProxy('http://localhost:1234/',
                         username='myuser',
                         password='secret',
                         user_agent='myprogram')
    retval = client.do_something('test')
    file_contents = client.__getfile__('myfile.pdf')
    batch = BatchCall(client)
    batch.do_something('call 1')
    batch.do_something('call 2')
    batch()

