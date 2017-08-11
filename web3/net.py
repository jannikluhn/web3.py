class Net(object):

    def __init__(self, web3):
        self.web3 = web3

    @property
    def listening(self):
        return self.web3.manager.request_blocking("net_listening", [])

    def getListening(self, *args, **kwargs):
        raise NotImplementedError("Async calling has not been implemented")

    @property
    def peerCount(self):
        return self.web3.manager.request_blocking("net_peerCount", [])

    def getPeerCount(self, *args, **kwargs):
        raise NotImplementedError("Async calling has not been implemented")
