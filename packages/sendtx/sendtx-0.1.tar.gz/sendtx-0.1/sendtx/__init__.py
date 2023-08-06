#!/usr/bin/python
import sys
import multiprocessing
from twisted.internet import reactor
from twisted.internet.protocol import ClientFactory
import StringIO
import binascii
import halfnode

success = False

def send_failed():
    global success
    success = False
    reactor.stop()
    
class P2PProtocol(halfnode.BitcoinP2PProtocol):
    def __init__(self, tx):
        self.tx = tx
        self.sent = False
        
    def connectionMade(self):
        halfnode.BitcoinP2PProtocol.connectionMade(self)
        self.broadcast_tx(self.tx)

    def connectionLost(self, reason):
        reactor.stop()
        
    def got_message(self, message):
        halfnode.BitcoinP2PProtocol.got_message(self, message)
        if self.sent:
            global success
            success = True
            self.transport.loseConnection()
        
    def broadcast_tx(self, txdata):
        '''Broadcast new transaction (as a hex stream) to trusted node'''
        tx = halfnode.msg_tx()
        tx.deserialize(StringIO.StringIO(binascii.unhexlify(txdata)))
        tx.tx.calc_sha256()
        #print "%x" % tx.tx.sha256
        self.send_message(tx)
        self.sent = True
        
class P2PFactory(ClientFactory):
    def __init__(self, tx):
        self.tx = tx
        
    def buildProtocol(self, addr):
        return P2PProtocol(self.tx)

def _process(host, tx):
    reactor.connectTCP(host, 8333, P2PFactory(tx))
    reactor.callLater(10, send_failed)
    reactor.run()
    
    global success
    if success == True:
        sys.exit(42)
        
def process_args():
    args = sys.argv[1:]
    if len(args) != 2:
        print "Usage: ./sendtx.py <bitcoin_node_hostname> <serialized_tx>"
        print "Example: ./sendtx.py localhost 01000000015210999277896c1a0c49c3071b6b2448d1d98c9880aefe50c0d00e79fa40ad64010000008b48304502207bb45481d4674837773878b184c7a59ebd3c87095322106355057411f89bd0ec02210084690f4b0ea00eeb8ad2c12ee603057433d04812317a65ea84aa605b5f643815014104e6a069738d8e8491a8abd3bed7d303c9b2dc3792173a18483653036fd74a5100fc6ee327b6a82b3df79005f101b88496988fa414af32df11fff3e96d53d26d03ffffffff0240420f00000000001976a914e1c9b052561cf0a1da9ee3175df7d5a2d7ff7dd488aca0252600000000001976a914f01ef5b20f08b93773c1152c5481a6e2d527096e88ac00000000"
        sys.exit()

    _process(args[0], args[1])

def process(host, tx):
    p = multiprocessing.Process(target=_process, args=(host, tx,))
    p.start()
    p.join()
    if p.exitcode != 42:
        raise Exception("Transaction broadcasting failed")
    
if __name__ == '__main__':
    process_args()
    #process('localhost2', '01000000015210999277896c1a0c49c3071b6b2448d1d98c9880aefe50c0d00e79fa40ad64010000008b48304502207bb45481d4674837773878b184c7a59ebd3c87095322106355057411f89bd0ec02210084690f4b0ea00eeb8ad2c12ee603057433d04812317a65ea84aa605b5f643815014104e6a069738d8e8491a8abd3bed7d303c9b2dc3792173a18483653036fd74a5100fc6ee327b6a82b3df79005f101b88496988fa414af32df11fff3e96d53d26d03ffffffff0240420f00000000001976a914e1c9b052561cf0a1da9ee3175df7d5a2d7ff7dd488aca0252600000000001976a914f01ef5b20f08b93773c1152c5481a6e2d527096e88ac00000000')