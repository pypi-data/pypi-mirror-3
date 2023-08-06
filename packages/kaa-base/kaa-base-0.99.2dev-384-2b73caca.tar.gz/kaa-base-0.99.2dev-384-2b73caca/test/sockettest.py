import logging
import kaa
from kaa.net.tls import TLSSocket, TLSContext

log = logging.getLogger('tls').ensureRootHandler()
#log = logging.getLogger('base').setLevel(logging.DEBUG2)

session = None
# Keep a single global socket so we can reuse sessions.
remote = TLSSocket(reuse_sessions=True)

@kaa.coroutine()
def new_client(client):
    global session, remote
    ip, port = client.peer[:2]
    print 'New connection from %s:%s' % (ip, port)
    #yield client.starttls_server()
    yield client.starttls_server(ticket_key='x'*48)
    print 'REUSED CLIENT?', client.session_reused
    client.write('Hello %s, connecting from port %d\n' % (ip, port))

    #remote = TLSSocket()
    #yield remote.connect('www.google.com:443')
    yield remote.connect('urandom.ca:443')
    print 'Conneced to remote'
    try:
        yield remote.starttls_client()
        print 'REUSED SERVER?', remote.session_reused
        yield remote.write('GET / HTTP/1.0\n\n')
        print 'Wrote request'
        while remote.readable:
            data = yield remote.read()
            yield client.write(data)
        client.write('\n\nBye!\n')
    finally:
        print 'close client'
        remote.close()
        #client.close()

    while client.readable:
        print (yield client.read())
server = kaa.Socket()
server = TLSSocket()
server.ctx.load_cert_chain('/home/tack/foo.urandom.ca.rapidssl.2012.crt', '/home/tack/foo.urandom.ca.rapidssl.2012.key.nopass')
#server.ctx.ticket_key = 'x'*48
server.signals['new-client'].connect(new_client)
server.listen(8080)
print "Connect to localhost:8080"
kaa.main.run()
