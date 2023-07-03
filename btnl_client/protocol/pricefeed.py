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
    TRADE_FORMAT_STR = '<cQQcqI'

    @classmethod
    def from_btp(cls, data: bytes) -> "Trade":
        (
            message_type,
            ack_id,
            product_id,
            taker_side,
            price,
            quantity,
        ) = struct.unpack(Trade.TRADE_FORMAT_STR, data)
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
    LEVEL_FORMAT_STR = "<cQQcqI"

    @classmethod
    def from_btp(cls, data: bytes) -> "Level":
        (
            message_type,
            ack_id,
            product_id,
            side,
            price,
            quantity,
        ) = struct.unpack(Level.LEVEL_FORMAT_STR, data)
        assert message_type == Level.MSG_TYPE
        return Level(ack_id, product_id, side, price, quantity)


@dataclass
class BookLevel:
    price: int
    quantity: int

    BOOK_LEVEL_FORMAT_STR = '<qI'


@dataclass
class Book(MessageBody):
    last_ack_id: int
    product_id: int
    bids: List[BookLevel]
    asks: List[BookLevel]

    body_encoding = BodyEncoding.Pricefeed
    MSG_TYPE = b"B"
    BOOK_HEADER_FORMAT_STR = '<cQQ'
    BID_ASK_LEVELS_LENGTH_FORMAT_STR = '<I'

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
            data[fixed_length_size : fixed_length_size + bid_ask_length_size])[0]

        # calculate book level size
        book_level_size = struct.calcsize(BookLevel.BOOK_LEVEL_FORMAT_STR)

        # parse bid data
        bid_data = data[fixed_length_size + bid_ask_length_size : fixed_length_size + bid_ask_length_size + bids_length]
        bids = []
        while len(bid_data) > 0:
            book_level = struct.unpack(BookLevel.BOOK_LEVEL_FORMAT_STR, bid_data[:book_level_size])
            bids.append(book_level)

            bid_data = bid_data[book_level_size:]
            if len(bid_data) <= book_level_size:
                break

        # calculate asks length
        asks_length_index = fixed_length_size + bid_ask_length_size + bids_length
        asks_length = struct.unpack(
            Book.BID_ASK_LEVELS_LENGTH_FORMAT_STR,
            data[asks_length_index : asks_length_index + bid_ask_length_size])[0]
        ask_data = data[asks_length_index + bid_ask_length_size : asks_length_index + bid_ask_length_size + asks_length]

        asks = []
        while len(ask_data) > 0:
            book_level = struct.unpack(BookLevel.BOOK_LEVEL_FORMAT_STR, ask_data[:book_level_size])
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
    BLOCK_FORMAT_STR = "<cQQqI"

    @classmethod
    def from_btp(cls, data: bytes) -> "Block":
        (
            message_type,
            ack_id,
            product_id,
            price,
            quantity,
        ) = struct.unpack(Block.BLOCK_FORMAT_STR, data)
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
