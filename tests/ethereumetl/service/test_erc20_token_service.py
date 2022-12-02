import pytest

from ethereumetl.service.eth_erc20_token_service import EthERC20TokenService
import web3

from ethereumetl.thread_local_proxy import ThreadLocalProxy
from ethereumetl.web3_utils import build_web3
from tests.ethereumetl.job.helpers import get_web3_provider


def test_erc20_token_service():
    token_service = EthERC20TokenService(ThreadLocalProxy(lambda: build_web3(get_web3_provider('infura'))))

    token = token_service.get_token('0xdAC17F958D2ee523a2206206994597C13D831ec7'.lower())
    assert token.symbol== 'USDT'
    assert token.name == 'Tether USD'
    assert token.decimals == 6
    assert token.total_supply == 32297366521996886

    token = token_service.get_token('0xB8c77482e45F1F44dE1745F52C74426C631bDD52'.lower())
    assert token.symbol== 'BNB'
    assert token.name == 'BNB'
    assert token.decimals == 18
    assert token.total_supply == 16579517055253348798759097
