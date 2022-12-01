from ethereumetl.jobs.export_tokens_base_job import ExportTokensBaseJob
from ethereumetl.mappers.erc1155_token_mapper import EthERC1155TokenMapper
from ethereumetl.service.eth_erc1155_token_service import EthERC1155TokenService


class ExportERC1155TokensJob(ExportTokensBaseJob):
    def __init__(self, web3, item_exporter, token_addresses_iterable, max_workers):
        super().__init__(web3, item_exporter, token_addresses_iterable, max_workers, EthERC1155TokenService, EthERC1155TokenMapper)
