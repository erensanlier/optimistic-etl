import pytest

from ethereumetl.service.eth_erc1155_token_service import EthERC1155TokenService
import web3

from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import build_web3
from tests.ethereumetl.job.helpers import get_web3_provider


def test_erc1155_token_service():
    token_service = EthERC1155TokenService(ThreadLocalProxy(lambda: build_web3(get_web3_provider('infura'))))

    token = token_service.get_token('0x54b743D6055e3BBBF13eb2C748A3783516156e5B'.lower())
    assert token.address == '0x54b743D6055e3BBBF13eb2C748A3783516156e5B'.lower()

