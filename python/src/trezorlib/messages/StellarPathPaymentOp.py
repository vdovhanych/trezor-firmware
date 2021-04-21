# Automatically generated by pb2py
# fmt: off
# isort:skip_file
from .. import protobuf as p

from .StellarAssetType import StellarAssetType

if __debug__:
    try:
        from typing import Dict, List, Optional  # noqa: F401
        from typing_extensions import Literal  # noqa: F401
    except ImportError:
        pass


class StellarPathPaymentOp(p.MessageType):
    MESSAGE_WIRE_TYPE = 212

    def __init__(
        self,
        *,
        paths: Optional[List[StellarAssetType]] = None,
        source_account: Optional[str] = None,
        send_asset: Optional[StellarAssetType] = None,
        send_max: Optional[int] = None,
        destination_account: Optional[str] = None,
        destination_asset: Optional[StellarAssetType] = None,
        destination_amount: Optional[int] = None,
    ) -> None:
        self.paths = paths if paths is not None else []
        self.source_account = source_account
        self.send_asset = send_asset
        self.send_max = send_max
        self.destination_account = destination_account
        self.destination_asset = destination_asset
        self.destination_amount = destination_amount

    @classmethod
    def get_fields(cls) -> Dict:
        return {
            1: ('source_account', p.UnicodeType, None),
            2: ('send_asset', StellarAssetType, None),
            3: ('send_max', p.SVarintType, None),
            4: ('destination_account', p.UnicodeType, None),
            5: ('destination_asset', StellarAssetType, None),
            6: ('destination_amount', p.SVarintType, None),
            7: ('paths', StellarAssetType, p.FLAG_REPEATED),
        }
