from ethereumetl.jobs.export_tokens_base_job import ExportTokensBaseJob
from ethereumetl.mappers.erc20_token_mapper import EthERC20TokenMapper
from ethereumetl.service.eth_erc20_token_service import EthERC20TokenService


class ExportERC20TokensJob(ExportTokensBaseJob):
    def __init__(self, web3, item_exporter, token_addresses_iterable, max_workers):
        super().__init__(web3, item_exporter, token_addresses_iterable, max_workers, EthERC20TokenService, EthERC20TokenMapper)
