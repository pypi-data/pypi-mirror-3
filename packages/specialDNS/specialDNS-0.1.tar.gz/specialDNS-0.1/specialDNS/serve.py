"""
@guy who gave me this: Jochen Ritzel
"""

import info
import extraresolver

import sys,os
sys.path.append(os.path.join(*(os.path.expanduser("~"),".local","lib","python2.7","site-packages")))

tries = 0
while True:
    try:
        from twisted.names import dns, server, client, cache, error, common
        from twisted.application import service, internet
        from twisted.internet.error import CannotListenError
        from twisted.internet import defer
        # twisted.names sucks at finding system nameservers.
        break
    except ImportError, e:
        if tries == 2: raise e
        tries += 1
        import sys,setup
        sys.argv = ["build", "install"]
        setup.main()

def guessPort(name):
    import socket
    service,proto,rest = name.split(".",2)
    service = service[1:]
    proto = proto[1:]
    print service,proto
    return socket.getservbyname(service,proto)
    

class NameSubstitutor(client.Resolver):
    """
    Resolves names by looking in a mapping. 
    If `name in mapping` then mapping[name] should return a IP
    else the next server in servers will be asked for name    
    """
    def __init__(self):
        client.Resolver.__init__(self,resolv='/dev/null')
        self.ttl = 10
        self.lookup = ()
    def gotIP(self,rr,suffix):
        # XXX: our own IP can't be IPv6 eh
        # ip = rr[0][0].payload.dottedquad
        ip = rr
        print "Got the IP of",suffix,ip
        self.lookup += ((suffix,ip),)
    def query(self,query,timeout=None):
        name = query.name.name        
        print "Looking up",name,common.typeToMethod[query.type]
        for suffix,ip in self.lookup:
            if name.endswith('.'+suffix) or name == suffix:
                if query.type == dns.A:
                    record = dns.Record_A(ip,self.ttl)
                elif query.type == dns.SRV:
                    port = guessPort(name)
                    record = dns.Record_SRV(port=port,target=suffix,ttl=self.ttl)
                elif query.type == dns.MX:
                    record = dns.Record_MX(name=suffix,ttl=self.ttl)
                elif query.type == dns.NS:
                    record = dns.Record_NS(name=suffix,ttl=self.ttl)
                else:
                    return defer.fail(error.AuthoritativeDomainError("Fuck da police"))
            
                response = [dns.RRHeader(name, query.type, dns.IN, self.ttl, record)]
                print "yay",response

                return defer.succeed((response,response,[]))
                
        return client.Resolver.query(self,query,timeout)

localThing = '127.0.0.1' # 127.0.0.2 sigh...

# twistd sucks!
def main():
    from twisted.application.app import startApplication
    from twisted.internet import reactor
    ports = iter((53,10053))
    def tryNextPort():
        try:
            port = ports.next()
        except StopIteration:
            print "Ran outta piddies"
            raise SystemExit

        resolver = NameSubstitutor()
        f = server.DNSServerFactory(caches=[cache.CacheResolver()], clients=[resolver])
        #f = server.DNSServerFactory(clients=[resolver])
        p = dns.DNSDatagramProtocol(f)
        f.noisy = p.noisy = False

        # register as tcp and udp
        ret = service.MultiService()

        # 127.0.0.2 to avoid conflict with an existing local DNS
        # ...which still fails if that DNS is on *:53 but oh well.
        # XXX: doesn't work for UDP except netcat UDP
        for (klass, arg) in [(internet.TCPServer, f), (internet.UDPServer, p)]:
            s = klass(port, arg,interface=localThing)
            s.setServiceParent(ret)
        # run all of the above as a twistd application
        application = service.Application('dnsserver', 1, 1)
        ret.setServiceParent(service.IServiceCollection(application))

        try:
            startApplication(application,False)
        except CannotListenError,e:
            print '******',e
            tryNextPort()
            return

        names = iter(info.names)

        if port==53: 
            extraresolver.nameservers.discard(localThing)
            # This is after localThing was removed but before
            # 8.8.8.8 etc were added on.
            extraresolver.recoverLast()
            extraresolver.nameservers.discard(localThing)
            extraresolver.setResolver(localThing)
        else:
            # This is before
            # 8.8.8.8 etc were added on.
            extraresolver.recoverLast()

        parentResolver = client.Resolver(resolv='/dev/null')
        afraidResolver = client.Resolver(resolv='/dev/null')

        def lookupAnother(*nun):
            resolver.servers = list((n,53) for n in extraresolver.nameservers)
            try:
                os.setregid(65535,65535)
                os.setreuid(65535,65535)
            except OSError: pass
                                    
            try:
                name = names.next()
            except StopIteration: 
                print "Your DNS workaround server is now running."
                print "Set your DNS to",localThing,"at port",port
                print "(If it's 53 that's the default so don't need to set the port.)"
                return
            print "Trying",name
            def findIP(rr):
                return rr[0][0].payload.dottedQuad()       
            afraidResolver.lookupAddress(name)\
                .addCallback(findIP).addCallback(resolver.gotIP,name).addCallbacks(lookupAnother,lookupAnother)

        def foundAfraid(rr,timeout=None):
            afraidResolver.servers = [(rr[0][0].payload.dottedQuad(),53)]
            lookupAnother()

        if len(extraresolver.nameservers)==0:
            print "WARNING: You do not seem to have any nameservers! Using some (slow (possibly overloaded)) defaults."
            # should Google really only be a last ditch last ditch effort?
            # heh heh yeah
            extraresolver.nameservers.update(('8.8.8.8','198.41.0.4','192.228.79.201'))
            parentResolver.servers=list((n,53) for n in extraresolver.nameservers)
            parentResolver.lookupAddress(info.trustedNS).addCallback(foundAfraid)
        else:
            extraresolver.recoverLast()
            parentResolver.servers=list((n,53) for n in extraresolver.nameservers)
            parentResolver.lookupAddress(info.trustedNS).addCallback(foundAfraid)   
    reactor.callLater(0,tryNextPort)
    reactor.run()

if __name__ == '__main__': main()
