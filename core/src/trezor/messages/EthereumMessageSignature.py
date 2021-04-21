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


class EthereumMessageSignature(p.MessageType):
    MESSAGE_WIRE_TYPE = 66

    def __init__(
        self,
        *,
        signature: bytes,
        address: str,
    ) -> None:
        self.signature = signature
        self.address = address

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            2: ('signature', p.BytesType, p.FLAG_REQUIRED),
            3: ('address', p.UnicodeType, p.FLAG_REQUIRED),
        }
