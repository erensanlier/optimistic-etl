import logging

logger = logging.getLogger('eth_token_service')

from web3.exceptions import BadFunctionCallOutput, ContractLogicError


class EthBaseTokenService(object):
    def __init__(self, web3, function_call_result_transformer=None):
        self._function_call_result_transformer = function_call_result_transformer
        self._web3 = web3

    def _get_first_result(self, *funcs):
        for func in funcs:
            result = self._call_contract_function(func)
            if result is not None:
                return result
        return None

    def _call_contract_function(self, func):
        # BadFunctionCallOutput exception happens if the token doesn't implement a particular function
        # or was self-destructed
        # OverflowError exception happens if the return type of the function doesn't match the expected type
        result = call_contract_function(
            func=func,
            ignore_errors=(BadFunctionCallOutput, ContractLogicError, OverflowError, ValueError),
            default_value=None)

        if self._function_call_result_transformer is not None:
            return self._function_call_result_transformer(result)
        else:
            return result

    def _bytes_to_string(self, b, ignore_errors=True):
        if b is None:
            return b

        try:
            b = b.decode('utf-8')
        except UnicodeDecodeError as e:
            if ignore_errors:
                logger.debug('A UnicodeDecodeError exception occurred while trying to decode bytes to string',
                             exc_info=True)
                b = None
            else:
                raise e

        if self._function_call_result_transformer is not None:
            b = self._function_call_result_transformer(b)
        return b


def call_contract_function(func, ignore_errors, default_value=None):
    try:
        result = func.call()
        return result
    except Exception as ex:
        if type(ex) in ignore_errors:
            logger.debug('An exception occurred in function {} of contract {}. '.format(func.fn_name, func.address)
                         + 'This exception can be safely ignored.', exc_info=True)
            return default_value
        else:
            raise ex
