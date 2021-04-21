# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class TezosOriginationOp(p.MessageType):

    def __init__(
        self,
        *,
        source: bytes,
        fee: int,
        counter: int,
        gas_limit: int,
        storage_limit: int,
        balance: int,
        script: bytes,
        manager_pubkey: Optional[bytes] = None,
        spendable: Optional[bool] = None,
        delegatable: Optional[bool] = None,
        delegate: Optional[bytes] = None,
    ) -> None:
        self.source = source
        self.fee = fee
        self.counter = counter
        self.gas_limit = gas_limit
        self.storage_limit = storage_limit
        self.balance = balance
        self.script = script
        self.manager_pubkey = manager_pubkey
        self.spendable = spendable
        self.delegatable = delegatable
        self.delegate = delegate

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            12: ('source', p.BytesType, p.FLAG_REQUIRED),
            2: ('fee', p.UVarintType, p.FLAG_REQUIRED),
            3: ('counter', p.UVarintType, p.FLAG_REQUIRED),
            4: ('gas_limit', p.UVarintType, p.FLAG_REQUIRED),
            5: ('storage_limit', p.UVarintType, p.FLAG_REQUIRED),
            6: ('manager_pubkey', p.BytesType, None),
            7: ('balance', p.UVarintType, p.FLAG_REQUIRED),
            8: ('spendable', p.BoolType, None),
            9: ('delegatable', p.BoolType, None),
            10: ('delegate', p.BytesType, None),
            11: ('script', p.BytesType, p.FLAG_REQUIRED),
        }
