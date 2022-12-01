# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging

from web3.exceptions import BadFunctionCallOutput, ContractLogicError

from ethereumetl.domain.erc20_token import EthERC20Token
from ethereumetl.erc20_abi import ERC20_ABI, ERC20_ABI_ALTERNATIVE_1
from ethereumetl.service.eth_base_token_service import EthBaseTokenService

logger = logging.getLogger('eth_token_service')


class EthERC20TokenService(EthBaseTokenService):
    def __init__(self, web3, function_call_result_transformer=None):
        super().__init__(web3,function_call_result_transformer)

    def get_token(self, token_address):
        checksum_address = self._web3.toChecksumAddress(token_address)
        contract = self._web3.eth.contract(address=checksum_address, abi=ERC20_ABI)
        contract_alternative_1 = self._web3.eth.contract(address=checksum_address, abi=ERC20_ABI_ALTERNATIVE_1)

        symbol = self._get_first_result(
            contract.functions.symbol(),
            contract.functions.SYMBOL(),
            contract_alternative_1.functions.symbol(),
            contract_alternative_1.functions.SYMBOL(),
        )
        if isinstance(symbol, bytes):
            symbol = self._bytes_to_string(symbol)

        name = self._get_first_result(
            contract.functions.name(),
            contract.functions.NAME(),
            contract_alternative_1.functions.name(),
            contract_alternative_1.functions.NAME(),
        )
        if isinstance(name, bytes):
            name = self._bytes_to_string(name)

        decimals = self._get_first_result(contract.functions.decimals(), contract.functions.DECIMALS())
        total_supply = self._get_first_result(contract.functions.totalSupply())

        token = EthERC20Token()
        token.address = token_address
        token.symbol = symbol
        token.name = name
        token.decimals = decimals
        token.total_supply = total_supply

        return token