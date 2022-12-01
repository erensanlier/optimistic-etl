class EntityType:
    BLOCK = 'block'
    TRANSACTION = 'transaction'
    RECEIPT = 'receipt'
    LOG = 'log'
    ERC20_TRANSFER = 'erc20_transfer'
    ERC721_TRANSFER = 'erc721_transfer'
    ERC1155_TRANSFER = 'erc1155_transfer'
    TOKEN_TRANSFER = 'token_transfer'
    TRACE = 'trace'
    CONTRACT = 'contract'
    TOKEN = 'token'
    ERC20_TOKEN = 'erc20_token'
    ERC721_TOKEN = 'erc721_token'
    ERC1155_TOKEN = 'erc1155_token'
    ALL_FOR_STREAMING = [BLOCK, TRANSACTION, LOG, ERC20_TRANSFER, ERC721_TRANSFER, ERC1155_TRANSFER , TRACE, CONTRACT,  ERC20_TOKEN, ERC721_TOKEN, ERC1155_TOKEN]
    ALL_FOR_INFURA = [BLOCK, TRANSACTION, LOG, ERC20_TRANSFER, ERC721_TRANSFER, ERC1155_TRANSFER, ERC20_TOKEN, ERC721_TOKEN, ERC1155_TOKEN]
