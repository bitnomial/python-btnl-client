import requests
import json
from dataclasses import dataclass
from typing import List, Optional, Union
from enum import Enum


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


class BitnomialHttpClient:
    base_url: str
    env: str = "prod"

    def __init__(self, base_url=BASE_URL, env="prod"):
        self.base_url = base_url
        self.env = env

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
