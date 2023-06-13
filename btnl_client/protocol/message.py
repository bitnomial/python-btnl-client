import struct
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .core import BodyEncoding, MessageBody
from .login import Login
from .market_state import MarketStateUpdate
from .order_entry import OrderEntry


@dataclass
class Heartbeat(MessageBody):
    body_encoding = BodyEncoding.Heartbeat

    FORMAT_STR = ""

    def to_btp(self) -> bytes:
        return struct.pack(self.FORMAT_STR)

    @classmethod
    def from_btp(cls, data: bytes) -> "Heartbeat":
        return Heartbeat()


class DisconnectReason(Enum):
    SequenceIdFault = 0x01
    HeartbeatFault = 0x02
    FailedToLogin = 0x03
    MessagingRateExceeded = 0x04
    ParseFailure = 0x05


@dataclass
class Disconnect(MessageBody):
    disconnect_reason: DisconnectReason
    expected_sequence_id: Optional[int]
    actual_sequence_id: Optional[int]

    body_encoding = BodyEncoding.Disconnect
    FORMAT_STR = "<BII"

    def to_btp(self) -> bytes:
        return struct.pack(
            Disconnect.FORMAT_STR,
            self.disconnect_reason,
            self.expected_sequence_id if self.expected_sequence_id is not None else 0,
            self.actual_sequence_id if self.actual_sequence_id is not None else 0,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Disconnect":
        disconnect_reason, expected_sequence_id, actual_sequence_id = struct.unpack(
            Disconnect.FORMAT_STR, data
        )
        return Disconnect(
            DisconnectReason(disconnect_reason.decode()),
            expected_sequence_id if expected_sequence_id != 0 else None,
            actual_sequence_id if actual_sequence_id != 0 else None,
        )


@dataclass
class Header:
    sequence_id: int
    body_encoding: BodyEncoding
    body_length: int

    PROTOCOL_ID = b"BT"
    VERSION = 2
    FORMAT_STR = "<2sHI2sH"
    LEN = 12

    def to_btp(self) -> bytes:
        return struct.pack(
            Header.FORMAT_STR,
            Header.PROTOCOL_ID,  # Protocol ID
            Header.VERSION,  # Version
            self.sequence_id,  # Sequence ID
            self.body_encoding.value.encode(),  # Body Encoding
            self.body_length,  # Body Length
        )

    @staticmethod
    def from_btp(data: bytes) -> "Header":
        protocol_id, version, sequence_id, body_encoding, body_length = struct.unpack(
            Header.FORMAT_STR, data[: Header.LEN]
        )
        assert protocol_id == Header.PROTOCOL_ID
        assert version == Header.VERSION
        return Header(sequence_id, BodyEncoding(body_encoding.decode()), body_length)


@dataclass
class Message:
    header: Header
    body: MessageBody

    def to_btp(self) -> bytes:
        if self.body.body_encoding == BodyEncoding.Heartbeat:
            self.header.sequence_id = 0
        body_btp = self.body.to_btp()
        # maybe use struct.size?
        self.header.body_length = len(body_btp)
        return self.header.to_btp() + body_btp

    BODY_ENCODINGS = {
        BodyEncoding.Login: Login.from_btp,
        BodyEncoding.OrderEntry: OrderEntry.from_btp,
        BodyEncoding.MarketState: MarketStateUpdate.from_btp,
        BodyEncoding.Heartbeat: Heartbeat.from_btp,
        BodyEncoding.Disconnect: Disconnect.from_btp,
    }

    @staticmethod
    def from_btp(data: bytes) -> "Message":
        header = Header.from_btp(data[: Header.LEN])

        if header.body_encoding == BodyEncoding.Heartbeat:
            return Message(header, Heartbeat())

        parse_body = Message.BODY_ENCODINGS.get(header.body_encoding)
        if parse_body is None:
            raise ValueError(f"Unknown body encoding: {header}")

        body = data[Header.LEN : Header.LEN + header.body_length]
        parsed_body = parse_body(body)
        return Message(header, parsed_body)

    @staticmethod
    async def read_message(reader) -> "Message":
        header_data = await reader.readexactly(Header.LEN)
        header = Header.from_btp(header_data)

        if header.body_encoding == BodyEncoding.Heartbeat:
            return Message(header, Heartbeat())

        body_data = await reader.readexactly(header.body_length)

        assert len(body_data) == header.body_length
        parse_body = Message.BODY_ENCODINGS.get(header.body_encoding)
        if parse_body is None:
            raise ValueError(f"Unknown body encoding: {header}")
        parsed_body = parse_body(body_data)
        return Message(header, parsed_body)


def new_message(sequence_id, body) -> "Message":
    return Message(Header(sequence_id, body.body_encoding, 0), body)
