import struct
from dataclasses import dataclass
from typing import List

from .core import BodyEncoding, MessageBody, MessageTypeBody, Side


@dataclass
class Trade(MessageBody):
    ack_id: int
    product_id: int
    taker_side: Side
    price: int
    quantity: int

    body_encoding = BodyEncoding.Pricefeed
    MSG_TYPE = b"T"
    FORMAT_STR = "<cQQcqI"

    def to_btp(self) -> bytes:
        return struct.pack(
            Trade.FORMAT_STR,
            Trade.MSG_TYPE,
            self.ack_id,
            self.product_id,
            self.taker_side.value.encode(),
            self.price,
            self.quantity,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Trade":
        (
            message_type,
            ack_id,
            product_id,
            taker_side,
            price,
            quantity,
        ) = struct.unpack(Trade.FORMAT_STR, data)
        assert message_type == Trade.MSG_TYPE
        return Trade(ack_id, product_id, taker_side, price, quantity)


@dataclass
class Level(MessageBody):
    ack_id: int
    product_id: int
    side: Side
    price: int
    quantity: int

    body_encoding = BodyEncoding.Pricefeed
    MSG_TYPE = b"L"
    FORMAT_STR = "<cQQcqI"

    def to_btp(self) -> bytes:
        return struct.pack(
            Level.FORMAT_STR,
            Level.MSG_TYPE,
            self.ack_id,
            self.product_id,
            self.side,
            self.price,
            self.quantity,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Level":
        (
            message_type,
            ack_id,
            product_id,
            side,
            price,
            quantity,
        ) = struct.unpack(Level.FORMAT_STR, data)
        assert message_type == Level.MSG_TYPE
        return Level(ack_id, product_id, side, price, quantity)


@dataclass
class BookLevel:
    price: int
    quantity: int

    FORMAT_STR = "<qI"


@dataclass
class Book(MessageBody):
    last_ack_id: int
    product_id: int
    bids: List[BookLevel]
    asks: List[BookLevel]

    body_encoding = BodyEncoding.Pricefeed
    MSG_TYPE = b"B"
    BOOK_HEADER_FORMAT_STR = "<cQQ"
    BID_ASK_LEVELS_LENGTH_FORMAT_STR = "<I"

    def to_btp(self) -> bytes:
        # Create serialized bids and asks
        bids_btp = b"".join(
            [
                struct.pack(BookLevel.FORMAT_STR, bid.price, bid.quantity)
                for bid in self.bids
            ]
        )
        asks_btp = b"".join(
            [
                struct.pack(BookLevel.FORMAT_STR, ask.price, ask.quantity)
                for ask in self.asks
            ]
        )

        # Calculate lengths of bids and asks
        bids_len = len(bids_btp)
        asks_len = len(asks_btp)

        # Create book header
        header = struct.pack(
            Book.BOOK_HEADER_FORMAT_STR,
            Book.MSG_TYPE,
            self.last_ack_id,
            self.product_id,
        )

        # Append bids length, bids, asks length and asks to the header
        return (
            header
            + struct.pack(Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR, bids_len)
            + bids_btp
            + struct.pack(Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR, asks_len)
            + asks_btp
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Book":
        fixed_length_size = struct.calcsize(Book.BOOK_HEADER_FORMAT_STR)
        fixed_length_data = data[:fixed_length_size]
        (
            message_type,
            last_ack_id,
            product_id,
        ) = struct.unpack(Book.BOOK_HEADER_FORMAT_STR, fixed_length_data)
        assert message_type == Book.MSG_TYPE

        # calculate bids length
        bid_ask_length_size = struct.calcsize(Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR)
        bids_length = struct.unpack(
            Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR,
            data[fixed_length_size : fixed_length_size + bid_ask_length_size],
        )[0]

        # calculate book level size
        book_level_size = struct.calcsize(BookLevel.FORMAT_STR)

        # parse bid data
        bid_data = data[
            fixed_length_size
            + bid_ask_length_size : fixed_length_size
            + bid_ask_length_size
            + bids_length
        ]
        bids = []
        while len(bid_data) > 0:
            price, quantity = struct.unpack(
                BookLevel.FORMAT_STR, bid_data[:book_level_size]
            )
            book_level = BookLevel(price, quantity)
            bids.append(book_level)

            bid_data = bid_data[book_level_size:]
            if len(bid_data) <= book_level_size:
                break

        # calculate asks length
        asks_length_index = fixed_length_size + bid_ask_length_size + bids_length
        asks_length = struct.unpack(
            Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR,
            data[asks_length_index : asks_length_index + bid_ask_length_size],
        )[0]
        ask_data = data[
            asks_length_index
            + bid_ask_length_size : asks_length_index
            + bid_ask_length_size
            + asks_length
        ]

        asks = []
        while len(ask_data) > 0:
            price, quantity = struct.unpack(
                BookLevel.FORMAT_STR, ask_data[:book_level_size]
            )
            book_level = BookLevel(price, quantity)
            asks.append(book_level)

            ask_data = ask_data[book_level_size:]
            if len(ask_data) <= book_level_size:
                break

        return Book(
            last_ack_id,
            product_id,
            bids,
            asks,
        )


@dataclass
class Block(MessageBody):
    ack_id: int
    product_id: int
    price: int
    quantity: int

    body_encoding = BodyEncoding.Pricefeed
    MSG_TYPE = b"X"
    FORMAT_STR = "<cQQqI"

    def to_btp(self) -> bytes:
        return struct.pack(
            Block.FORMAT_STR,
            Block.MSG_TYPE,
            self.ack_id,
            self.product_id,
            self.price,
            self.quantity,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "Block":
        (
            message_type,
            ack_id,
            product_id,
            price,
            quantity,
        ) = struct.unpack(Block.FORMAT_STR, data)
        assert message_type == Block.MSG_TYPE
        return Block(ack_id, product_id, price, quantity)


@dataclass
class Pricefeed(MessageTypeBody):
    body_encoding = BodyEncoding.Pricefeed

    MESSAGE_TYPES = {
        Trade.MSG_TYPE: Trade.from_btp,
        Level.MSG_TYPE: Level.from_btp,
        Book.MSG_TYPE: Book.from_btp,
        Block.MSG_TYPE: Block.from_btp,
    }
