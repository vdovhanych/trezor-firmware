# Automatically generated by pb2py
# fmt: off
# isort:skip_file
import protobuf as p

from .PrevTx import PrevTx

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class TxAckPrevMeta(p.MessageType):
    MESSAGE_WIRE_TYPE = 22

    def __init__(
        self,
        *,
        tx: PrevTx,
    ) -> None:
        self.tx = tx

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('tx', PrevTx, p.FLAG_REQUIRED),
        }
