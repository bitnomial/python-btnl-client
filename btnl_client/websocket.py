import asyncio
import json
from dataclasses import dataclass
import dataclasses
from typing import List, Tuple, Union
from enum import Enum
import websockets


WEBSOCKET_URI = "wss://bitnomial.com/exchange/ws"


class ChannelName(Enum):
    Trade = "trade"
    Book = "book"
    Block = "block"
    Status = "status"


@dataclass
class Channel:
    name: ChannelName
    product_codes: List[str]


class SubscribeType(Enum):
    Subscribe = "subscribe"
    Unsubscribe = "unsubscribe"


@dataclass
class SubscribeMessage:
    type: SubscribeType
    product_codes: List[str]
    channels: List[Channel]


@dataclass
class DisconnectMessage:
    type: str  # always "disconnect"
    reason: str


class MessageType(Enum):
    Trade = "trade"
    Level = "level"
    Book = "book"
    Block = "block"
    Status = "status"


@dataclass
class Trade:
    type: MessageType
    ack_id: str
    price: int
    quantity: int
    symbol: str
    taker_side: str
    timestamp: str


@dataclass
class Level:
    type: MessageType
    ack_id: str
    price: int
    quantity: int
    side: str
    symbol: str
    timestamp: str


@dataclass
class Book:
    type: MessageType
    ack_id: str
    asks: List[Tuple[int, int]]
    bids: List[Tuple[int, int]]
    symbol: str
    timestamp: str


class Side(Enum):
    Bid = "Bid"
    Ask = "Ask"


@dataclass
class BlockTrade:
    type: MessageType
    ack_id: str
    leader_side: str
    price: int
    quantity: int
    symbol: str
    timestamp: str


class MarketStatus(Enum):
    Open = "Open"
    Halt = "Halt"
    Closed = "Closed"


@dataclass
class MarketStatusUpdate:
    type: MessageType
    ack_id: str
    state: MarketStatus
    symbol: str
    timestamp: str


Message = Union[Trade, Level, Book, BlockTrade, MarketStatusUpdate]


class DataclassEnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


def parse_message(message: str):
    data = json.loads(message)
    msg_type = MessageType(data["type"])
    if msg_type == MessageType.Trade:
        return Trade(**data)
    elif msg_type == MessageType.Level:
        return Level(**data)
    elif msg_type == MessageType.Book:
        return Book(**data)
    elif msg_type == MessageType.Block:
        return BlockTrade(**data)
    elif msg_type == MessageType.Status:
        return MarketStatusUpdate(**data)
    else:
        raise ValueError(f"Unknown channel: {msg_type}")


class BitnomialWebSocketClient:
    uri: str = WEBSOCKET_URI

    def __init__(self, uri=WEBSOCKET_URI):
        self.uri = uri

    async def connect(self, message: SubscribeMessage):
        async with websockets.connect(self.uri) as ws:
            await self.send_message(ws, message)
            await self.receive_message(ws)

    async def send_message(self, ws, message: SubscribeMessage):
        await ws.send(json.dumps(message, cls=DataclassEnumEncoder))

    async def receive_message(self, ws):
        async for message in ws:
            parsed_message = parse_message(message)
            self.handle_message(parsed_message)

    def run(self, message: SubscribeMessage):
        asyncio.run(self.connect(message))

    def handle_message(self, message: Message):
        print(message)


# Example use:
# client = BitnomialWebSocketClient("wss://bitnomial.com/exchange/ws")

# channels = [
#     Channel(name=ChannelName.Trade, product_codes=["BUI"]),
#     Channel(name=ChannelName.Book, product_codes=["BUI"]),
#     Channel(name=ChannelName.Status, product_codes=["BUI"]),
# ]

# message = SubscribeMessage(
#     type=SubscribeType.Subscribe, product_codes=["BUI", "BUSO"], channels=channels
# )

# client.run(message)
