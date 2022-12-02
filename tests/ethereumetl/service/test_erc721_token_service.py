import pytest

from ethereumetl.service.eth_erc721_token_service import EthERC721TokenService
import web3

from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import build_web3
from tests.ethereumetl.job.helpers import get_web3_provider


def test_erc721_token_service():
    token_service = EthERC721TokenService(ThreadLocalProxy(lambda: build_web3(get_web3_provider('infura'))))

    token = token_service.get_token('0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D'.lower())
    assert token.name == 'BoredApeYachtClub'
    assert token.symbol == 'BAYC'
    assert token.total_supply == 10000
    assert token.base_uri == "ipfs://QmeSjSinHpPnmXmspMjwiXyN6zS4E9zccariGR3jxcaWtq/"

