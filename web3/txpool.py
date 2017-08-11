class TxPool(object):
    def __init__(self, web3):
        self.web3 = web3

    @property
    def content(self):
        return self.web3.manager.request_blocking("txpool_content", [])

    @property
    def inspect(self):
        return self.web3.manager.request_blocking("txpool_inspect", [])

    @property
    def status(self):
        return self.web3.manager.request_blocking("txpool_status", [])
