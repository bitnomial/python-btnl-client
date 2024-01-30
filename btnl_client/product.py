from dataclasses import dataclass
from typing import Dict, List, Optional, Union, TypeVar, Generic
from enum import Enum
from datetime import datetime, date, timezone
import btnl_client.hmac as hmac
from urllib.parse import urlparse
import requests


BASE_URL = "https://bitnomial.com/exchange/api/v1"


class BaseSymbol(Enum):
    # only valid in env="prod"
    BUI = "BUI"
    BUS = "BUS"
    # only valid in env="sandbox"
    ZZZ = "ZZZ"


class ProductStatus(Enum):
    Active = "active"
    Forthcoming = "forthcoming"
    Expired = "expired"


class ProductSpecType(Enum):
    Future = "future"
    Spread = "spread"
    Option = "option"


@dataclass
class SpreadSpecLeg:
    product_id: int
    weight: int


@dataclass
class BaseProductSpec:
    type: ProductSpecType
    product_id: int
    product_name: str
    max_order_quantity: int
    min_block_size: int
    price_band_variation: int
    price_limit_percentage: float
    price_increment: int
    first_trading_day: str
    final_settle_time: str
    daily_open_time: str
    daily_settle_time: str
    symbol: str
    cqg_symbol: str
    product_status: ProductStatus
    base_symbol: BaseSymbol


@dataclass
class ProductFutureSpec(BaseProductSpec):
    margin_unit: str
    settlement_method: str
    contract_size: int
    contract_size_unit: str
    price_quotation_unit: str
    month: int
    year: int


@dataclass
class ProductSpreadSpec(BaseProductSpec):
    legs: List[SpreadSpecLeg]


@dataclass
class ProductOptionSpec(BaseProductSpec):
    underlying_product: int
    strike_price: float
    option_type: str


ProductSpec = Union[ProductFutureSpec, ProductOptionSpec, ProductSpreadSpec]


class ProductType(Enum):
    Future = "Future"
    Spread = "Spread"
    Option = "Option"


class Side(Enum):
    Bid = "Bid"
    Ask = "Ask"


class TimeInForce(Enum):
    IOC = "IOC"
    Day = "Day"
    GTC = "GTC"


class OrderStatus(Enum):
    Working = "Working"
    Closed = "Closed"


class Liquidity(Enum):
    Add = "Add"
    Remove = "Remove"
    SpreadLeg = "SpreadLeg"


@dataclass
class Order:
    symbol: str
    product_id: int
    product_type: ProductType
    id: int
    connection_id: int
    clearing_firm_code: str
    account_id: str
    open_ack_id: int
    side: Side
    price: int
    quantity_requested: int
    quantity_filled: int
    status: OrderStatus
    time_in_force: TimeInForce


@dataclass
class Fill:
    symbol: str
    product_id: int
    product_type: ProductType
    order_id: int
    clearing_firm_code: str
    time: datetime
    connection_id: int
    account_id: str
    ack_id: int
    side: Side
    price: int
    quantity_requested: int
    quantity_filled: int
    liquidity: Liquidity


class BlockTradeStatus(Enum):
    Pending = "Pending"
    Canceled = "Canceled"
    Rejected = "Rejected"
    Confirmed = "Confirmed"
    Accepted = "Accepted"


@dataclass
class BlockTrade:
    account_id: str
    block_trade_id: int
    counterparty_id: str
    counterparty_email: Optional[str]
    symbol: str
    side: Side
    price: int
    quantity: int
    exec_time: datetime
    report_time: datetime
    status: BlockTradeStatus
    status_reason: Optional[str]
    status_time: Optional[datetime]


@dataclass
class ProductData:
    product_id: int
    last_price_time: Optional[str]
    last_price: Optional[float]
    settlement_time: Optional[str]
    settlement_price: Optional[float]
    settlement_price_comment: Optional[str]
    open_price: Optional[float]
    high_price: Optional[float]
    low_price: Optional[float]
    close_price: Optional[float]
    price_change: Optional[float]
    volume: Optional[float]
    notional_volume: Optional[float]
    block_volume: Optional[float]
    notional_block_volume: Optional[float]
    price_limit_upper: float
    price_limit_lower: float
    open_interest: Optional[float]
    open_interest_change: Optional[float]


class Ordering:
    Asc = "asc"
    Desc = "desc"


T = TypeVar("T")
P = TypeVar("P")


@dataclass
class Pagination(Generic[T, P]):
    data: List[T]
    pagination: P


@dataclass
class CursorInfo:
    cursor: str


class BitnomialHttpClient:
    base_url: str
    env: str

    def __init__(self, base_url=None, env=None):
        self.base_url = base_url or BASE_URL
        self.env = env or "prod"

    def get_product_spec(
        self, product_id, day=None, active=None, base_symbol=None
    ) -> ProductSpec:
        url = self.base_url + f"/{self.env}/product/spec/{product_id}"
        params = {"day": day, "active": active, "base_symbol": base_symbol}
        response = requests.get(url, params=params)
        spec = response.json()
        spec_type = ProductSpecType(spec["type"])
        product_spec: ProductSpec
        if spec_type == ProductSpecType.Future:
            product_spec = ProductFutureSpec(**spec)
        elif spec_type == ProductSpecType.Spread:
            product_spec = ProductSpreadSpec(**spec)
        elif spec_type == ProductSpecType.Option:
            product_spec = ProductOptionSpec(**spec)
        else:
            raise ValueError(f"Unexpected product spec type: {spec['type']}")
        return product_spec

    def get_product_specs(
        self, day=None, active=None, base_symbol=None
    ) -> List[ProductSpec]:
        url = self.base_url + f"/{self.env}/product/specs"
        params = {"day": day, "active": active, "base_symbol": base_symbol}
        response = requests.get(url, params=params)
        product_specs: List[ProductSpec] = []
        for spec in response.json():
            spec_type = ProductSpecType(spec["type"])
            if spec_type == ProductSpecType.Future:
                product_specs.append(ProductFutureSpec(**spec))
            elif spec_type == ProductSpecType.Spread:
                product_specs.append(ProductSpreadSpec(**spec))
            elif spec_type == ProductSpecType.Option:
                product_specs.append(ProductOptionSpec(**spec))
            else:
                raise ValueError(f"Unexpected product spec type: {spec['type']}")
        return product_specs

    def get_product_data(
        self, day=None, active=None, base_symbol=None
    ) -> List[ProductData]:
        url = self.base_url + f"/{self.env}/product/data"
        params = {"day": day, "active": active, "base_symbol": base_symbol}
        response = requests.get(url, params=params)
        return [ProductData(**data) for data in response.json()]

    def get_product_datum(
        self, product_id, day=None, active=None, base_symbol=None
    ) -> ProductData:
        url = self.base_url + f"/{self.env}/product/data/{product_id}"
        params = {"day": day, "active": active, "base_symbol": base_symbol}
        response = requests.get(url, params=params)
        product_data = response.json()
        return ProductData(**product_data)


class AuthBitnomialHttpClient(BitnomialHttpClient):
    connection_id: int
    auth_token: str

    def __init__(self, connection_id, auth_token, base_url=None, env=None):
        self.connection_id = connection_id
        self.auth_token = auth_token
        super().__init__(base_url, env)

    def get_fills(
        self,
        symbols: Optional[List[str]] = None,
        product_ids: Optional[List[int]] = None,
        product_types: Optional[List[ProductType]] = None,
        clearing_firm_codes: Optional[List[str]] = None,
        account_ids: Optional[List[str]] = None,
        connection_ids: Optional[List[int]] = None,
        day: Optional[date] = None,
        limit=None,
        begin_time=None,
        end_time=None,
        order=None,
        cursor=None,
    ) -> Pagination[List[Fill], CursorInfo]:
        method = "GET"
        path = f"/{self.env}/fills"
        url = self.base_url + path
        params = {
            "symbol": symbols,
            "connection_id": connection_ids,
            "cursor": cursor,
            "order": order,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "day": day,
            "account_id": account_ids,
            "clearing_firm_code": clearing_firm_codes,
            "product_type": product_types,
            "product_id": product_ids,
        }
        headers = self.auth_headers(method, url, params)
        response = requests.get(url, params=params, headers=headers)
        fills = response.json()
        return Pagination(**fills)

    def get_orders(
        self,
        symbols: Optional[List[str]] = None,
        product_ids: Optional[List[int]] = None,
        product_types: Optional[List[ProductType]] = None,
        clearing_firm_codes: Optional[List[str]] = None,
        account_ids: Optional[List[str]] = None,
        connection_ids: Optional[List[int]] = None,
        day: Optional[date] = None,
        limit=None,
        begin_time=None,
        end_time=None,
        order=None,
        cursor=None,
    ) -> Pagination[List[Fill], CursorInfo]:
        method = "GET"
        path = f"/{self.env}/orders"
        url = self.base_url + path
        params = {
            "symbol": symbols,
            "connection_id": connection_ids,
            "product_id": product_ids,
            "account_id": account_ids,
            "clearing_firm_code": clearing_firm_codes,
            "product_type": product_types,
            "order": order,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "day": day,
            "cursor": cursor,
        }
        headers = self.auth_headers(method, url, params)
        response = requests.get(url, params=params, headers=headers)
        orders = response.json()
        return Pagination(**orders)

    def get_block_trades(
        self,
        symbols: Optional[List[str]] = None,
        product_ids: Optional[List[int]] = None,
        product_types: Optional[List[ProductType]] = None,
        clearing_firm_codes: Optional[List[str]] = None,
        account_ids: Optional[List[str]] = None,
        connection_ids: Optional[List[int]] = None,
        status: Optional[List[BlockTradeStatus]] = None,
        day: Optional[date] = None,
        limit=None,
        begin_time=None,
        end_time=None,
        order=None,
        cursor=None,
    ) -> Pagination[List[Fill], CursorInfo]:
        method = "GET"
        path = f"/{self.env}/block-trades"
        url = self.base_url + path
        params = {
            "symbol": symbols,
            "connection_id": connection_ids,
            "product_id": product_ids,
            "account_id": account_ids,
            "clearing_firm_code": clearing_firm_codes,
            "product_type": product_types,
            "status": status,
            "order": order,
            "begin_time": begin_time,
            "end_time": end_time,
            "limit": limit,
            "day": day,
            "cursor": cursor,
        }
        headers = self.auth_headers(method, url, params)
        response = requests.get(url, params=params, headers=headers)
        block_trades = response.json()
        return Pagination(**block_trades)

    def auth_headers(self, method: str, url: str, params: Dict):
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        path = urlparse(url).path
        signature = hmac.signature(
            method, path, params, timestamp, self.connection_id, self.auth_token
        )

        return {
            hmac.CONNECTION_ID_HEADER: str(self.connection_id),
            hmac.TIMESTAMP_HEADER: timestamp,
            hmac.SIGNATURE_HEADER: signature,
        }


# Example use:
# client = BitnomialHttpClient()

# product_specs = client.get_product_specs(active=True, base_symbol="BUS")
# product_data = client.get_product_data()

# first_product_id = product_specs[0].product_id
# first_spec = client.get_product_spec(first_product_id)
# first_data = client.get_product_datum(first_product_id)

# print(product_specs)
# print(product_data)
# print(first_spec)
# print(first_data)
