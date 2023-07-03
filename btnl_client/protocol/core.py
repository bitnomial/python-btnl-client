from enum import Enum
from typing import Callable, Dict, Protocol


class Side(Enum):
    Bid = "B"
    Ask = "A"


class BodyEncoding(Enum):
    OrderEntry = "OE"
    Login = "LG"
    MarketState = "MS"
    Heartbeat = "HB"
    Disconnect = "DN"
    Pricefeed = "PF"


class MessageBody(Protocol):
    body_encoding: BodyEncoding

    def to_btp(self) -> bytes:
        ...

    @classmethod
    def from_btp(cls, data: bytes) -> "MessageBody":
        ...


class MessageTypeBody(MessageBody, Protocol):
    MESSAGE_TYPES: Dict[bytes, Callable[[bytes], MessageBody]]

    @classmethod
    def from_btp(cls, data: bytes) -> "MessageBody":
        message_type = data[0:1]
        parse_body = cls.MESSAGE_TYPES.get(message_type)
        if parse_body is None:
            raise ValueError(f"Unknown message type: {message_type!r}")
        parsed_body = parse_body(data)
        return parsed_body
