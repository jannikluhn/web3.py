from __future__ import absolute_import


class Version(object):
    def __init__(self, web3):
        self.web3 = web3

    @property
    def api(self):
        from web3 import __version__
        return __version__

    @property
    def node(self):
        return self.web3.manager.request_blocking("web3_clientVersion", [])

    @property
    def network(self):
        return self.web3.manager.request_blocking("net_version", [])

    @property
    def ethereum(self):
        return self.web3.manager.request_blocking("eth_protocolVersion", [])
