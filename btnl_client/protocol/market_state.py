import struct
from dataclasses import dataclass
from enum import Enum

from .core import BodyEncoding, MessageBody


class MarketState(Enum):
    Open = "O"
    Halt = "H"
    Closed = "C"


@dataclass
class MarketStateUpdate(MessageBody):
    market_state: MarketState
    ack_id: int
    product_id: int

    body_encoding = BodyEncoding.MarketState
    FORMAT_STR = "<cQQ"

    def to_btp(self) -> bytes:
        return struct.pack(
            MarketStateUpdate.FORMAT_STR,
            self.market_state.value.encode(),
            self.ack_id,
            self.product_id,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "MarketStateUpdate":
        market_state, ack_id, product_id = struct.unpack(
            MarketStateUpdate.FORMAT_STR, data
        )
        return MarketStateUpdate(MarketState(market_state.decode()), ack_id, product_id)
