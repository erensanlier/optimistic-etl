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
from ethereumetl.jobs.export_tokens_base_job import ExportTokensBaseJob
from ethereumetl.mappers.erc721_token_mapper import EthERC721TokenMapper
from ethereumetl.service.eth_contract_service import EthContractService
from ethereumetl.service.eth_erc721_token_service import EthERC721TokenService


class ExtractERC721TokensJob(ExportTokensBaseJob):
    def __init__(self, web3, item_exporter, contracts_iterable, max_workers):
        super().__init__(web3, item_exporter, [], max_workers, EthERC721TokenService, EthERC721TokenMapper)
        self.contracts_iterable = contracts_iterable

    def _export(self):
        self.batch_work_executor.execute(self.contracts_iterable, self._export_tokens_from_contracts)

    def _export_tokens_from_contracts(self, contracts):
        contract_service = EthContractService()
        tokens = [contract for contract in contracts if contract_service.is_erc721_contract(contract['function_sighashes'])]

        for contract in tokens:
            self._export_token(token_address=contract['address'], block_number=contract['block_number'])