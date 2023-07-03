import struct
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .core import BodyEncoding, MessageBody, MessageTypeBody, Side


class TimeInForce(Enum):
    Day = "D"
    IOC = "I"


@dataclass
class Open(MessageBody):
    order_id: int
    product_id: int
    side: Side
    price: int
    quantity: int
    time_in_force: TimeInForce

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"O"
    FORMAT_STR = "<cQQcqIc"

    def to_btp(self) -> bytes:
        return struct.pack(
            Open.FORMAT_STR,
            Open.MSG_TYPE,  # Message type
            self.order_id,  # Order ID
            self.product_id,  # Product ID
            self.side.value.encode(),  # Side
            self.price,  # Price
            self.quantity,  # Quantity
            self.time_in_force.value.encode(),  # Time in force
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Open":
        (
            message_type,
            order_id,
            product_id,
            side,
            price,
            quantity,
            time_in_force,
        ) = struct.unpack(Open.FORMAT_STR, data)
        assert message_type == Open.MSG_TYPE
        return Open(
            order_id,
            product_id,
            Side(side.decode()),
            price,
            quantity,
            TimeInForce(time_in_force.decode()),
        )


@dataclass
class Modify(MessageBody):
    order_id: int
    modify_id: int
    price: int
    quantity: int

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"M"
    FORMAT_STR = "<cQQqI"

    def to_btp(self) -> bytes:
        return struct.pack(
            Modify.FORMAT_STR,
            Modify.MSG_TYPE,  # Message type
            self.order_id,  # Order ID
            self.modify_id,  # Modify ID
            self.price,  # Price
            self.quantity,  # Quantity
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Modify":
        (
            message_type,
            order_id,
            modify_id,
            price,
            quantity,
        ) = struct.unpack(Modify.FORMAT_STR, data)
        assert message_type == Modify.MSG_TYPE
        return Modify(
            order_id,
            modify_id,
            price,
            quantity,
        )


@dataclass
class Ack(MessageBody):
    ack_id: int
    order_id: int
    modify_id: Optional[int]  # note that we use Optional here to denote it can be NULL

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"A"
    FORMAT_STR = "<cQQQ"

    def to_btp(self) -> bytes:
        return struct.pack(
            Ack.FORMAT_STR,
            Ack.MSG_TYPE,
            self.ack_id,
            self.order_id,
            self.modify_id if self.modify_id is not None else 0,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Ack":
        message_type, ack_id, order_id, modify_id = struct.unpack(Ack.FORMAT_STR, data)
        assert message_type == Ack.MSG_TYPE
        return Ack(ack_id, order_id, modify_id if modify_id != 0 else None)


class RejectReason(Enum):
    AccountNotFound = 0x01
    ProductNotFound = 0x02
    OrderNotFound = 0x03
    OrderAlreadyExists = 0x04
    OrderAlreadyClosed = 0x05
    OrderNotChangedByModify = 0x06
    QuantityGreaterThanMaxOrderSize = 0x07
    QuantityLessThanMinOrderSize = 0x08
    PriceOutsidePriceBands = 0x09
    PriceOutsidePriceLimits = 0x0A
    PriceNotTickAligned = 0x0B
    MarketHalted = 0x0C
    MarketClosed = 0x0D
    GiveUpAccountNotFound = 0x0E
    GiveUpUnauthorized = 0x0F
    MessagingRateExceeded = 0x10
    PositionLimitExceeded = 0x11
    ConnectionDisabled = 0x12


@dataclass
class Reject(MessageBody):
    order_id: int
    modify_id: Optional[int]
    reject_reason: RejectReason

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"R"
    FORMAT_STR = "<cQQB"

    def to_btp(self) -> bytes:
        return struct.pack(
            Reject.FORMAT_STR,
            Reject.MSG_TYPE,
            self.order_id,
            # TODO is this right???
            self.modify_id if self.modify_id is not None else 0,
            self.reject_reason.value,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Reject":
        message_type, order_id, modify_id, reject_reason = struct.unpack(
            Reject.FORMAT_STR, data
        )
        assert message_type == Reject.MSG_TYPE
        return Reject(
            order_id, modify_id if modify_id != 0 else None, RejectReason(reject_reason)
        )


class CloseReason(Enum):
    IOCFinished = "I"
    NonConnectionCancel = "G"
    SelfMatchPreventionCanceled = "S"


@dataclass
class Close(MessageBody):
    ack_id: int
    order_id: int
    close_reason: CloseReason

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"C"
    FORMAT_STR = "<cQQc"

    def to_btp(self) -> bytes:
        return struct.pack(
            Close.FORMAT_STR,
            Close.MSG_TYPE,
            self.ack_id,
            self.order_id,
            self.close_reason.value.encode(),
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Close":
        message_type, ack_id, order_id, close_reason = struct.unpack(
            Close.FORMAT_STR, data
        )
        assert message_type == Close.MSG_TYPE
        return Close(ack_id, order_id, CloseReason(close_reason.decode()))


class Liquidity(Enum):
    Add = "A"
    Remove = "R"
    SpreadLegMatch = "S"


@dataclass
class Fill(MessageBody):
    ack_id: int
    order_id: int
    price: int
    quantity: int
    liquidity: Liquidity

    body_encoding = BodyEncoding.OrderEntry
    MSG_TYPE = b"F"
    FORMAT_STR = "<cQQIc"

    def to_btp(self) -> bytes:
        return struct.pack(
            Fill.FORMAT_STR,
            Fill.MSG_TYPE,
            self.ack_id,
            self.order_id,
            self.price,
            self.quantity,
            self.liquidity.value.encode(),
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Fill":
        message_type, ack_id, order_id, price, quantity, liquidity = struct.unpack(
            Fill.FORMAT_STR, data
        )
        assert message_type == Fill.MSG_TYPE
        return Fill(ack_id, order_id, price, quantity, Liquidity(liquidity.decode()))


@dataclass
class OrderEntry(MessageTypeBody):
    body_encoding = BodyEncoding.OrderEntry

    MESSAGE_TYPES = {
        Open.MSG_TYPE: Open.from_btp,
        Modify.MSG_TYPE: Modify.from_btp,
        Ack.MSG_TYPE: Ack.from_btp,
        Reject.MSG_TYPE: Reject.from_btp,
        Close.MSG_TYPE: Close.from_btp,
        Fill.MSG_TYPE: Fill.from_btp,
    }
