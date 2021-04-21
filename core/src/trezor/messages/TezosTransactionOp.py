# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

from .TezosContractID import TezosContractID
from .TezosParametersManager import TezosParametersManager

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class TezosTransactionOp(p.MessageType):

    def __init__(
        self,
        *,
        source: bytes,
        fee: int,
        counter: int,
        gas_limit: int,
        storage_limit: int,
        amount: int,
        destination: TezosContractID,
        parameters: Optional[bytes] = None,
        parameters_manager: Optional[TezosParametersManager] = None,
    ) -> None:
        self.source = source
        self.fee = fee
        self.counter = counter
        self.gas_limit = gas_limit
        self.storage_limit = storage_limit
        self.amount = amount
        self.destination = destination
        self.parameters = parameters
        self.parameters_manager = parameters_manager

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            9: ('source', p.BytesType, p.FLAG_REQUIRED),
            2: ('fee', p.UVarintType, p.FLAG_REQUIRED),
            3: ('counter', p.UVarintType, p.FLAG_REQUIRED),
            4: ('gas_limit', p.UVarintType, p.FLAG_REQUIRED),
            5: ('storage_limit', p.UVarintType, p.FLAG_REQUIRED),
            6: ('amount', p.UVarintType, p.FLAG_REQUIRED),
            7: ('destination', TezosContractID, p.FLAG_REQUIRED),
            8: ('parameters', p.BytesType, None),
            10: ('parameters_manager', TezosParametersManager, None),
        }
