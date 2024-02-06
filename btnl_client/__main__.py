import argparse
from btnl_client.product import BitnomialHttpClient, AuthBitnomialHttpClient
import btnl_client.product as web
from datetime import date, datetime


def get_parser():
    def add_public_args(p):
        p.add_argument("--day", type=date, dest="day", default=None)
        p.add_argument("--active", action="store_true", dest="active", default=None)
        p.add_argument("--base-symbol", type=str, dest="base_symbol", default=None)

    def add_auth_args(p):
        p.add_argument("connection_id", type=int)
        p.add_argument("auth_token", type=str)
        p.add_argument("--symbol", type=str, dest="symbols", action="append")
        p.add_argument("--cid", type=int, dest="connection_ids", action="append")
        p.add_argument("--pid", type=int, dest="product_ids", action="append")
        p.add_argument("--accid", type=str, dest="account_ids", action="append")
        p.add_argument("--clfc", type=str, dest="clearing_firm_codes", action="append")
        p.add_argument(
            "--product-types",
            type=web.ProductType,
            dest="product_types",
            action="append",
        )
        p.add_argument("--order", type=web.Ordering, dest="order")
        p.add_argument("--begin", type=datetime, dest="begin_time")
        p.add_argument("--end", type=datetime, dest="end_time")
        p.add_argument("--limit", type=int, dest="limit")
        p.add_argument("--day", type=date, dest="day")
        p.add_argument("--cursor", type=str, dest="cursor")

    parser = argparse.ArgumentParser(description="CLI BTNL client")
    parser.add_argument("--base-url", type=str, default=web.BASE_URL)
    parser.add_argument("--env", type=str, default="prod")
    command = parser.add_subparsers(dest="command", required=True)
    get_product_spec = command.add_parser("get-product-spec")
    get_product_spec.add_argument("product_id", type=int)
    add_public_args(get_product_spec)
    get_product_datum = command.add_parser("get-product-datum")
    get_product_datum.add_argument("product_id", type=int)
    add_public_args(get_product_datum)
    get_product_specs = command.add_parser("get-product-specs")
    add_public_args(get_product_specs)
    get_product_data = command.add_parser("get-product-data")
    add_public_args(get_product_data)
    get_orders = command.add_parser("get-orders")
    add_auth_args(get_orders)
    get_fills = command.add_parser("get-fills")
    add_auth_args(get_fills)
    get_fills = command.add_parser("get-block-trades")
    add_auth_args(get_fills)
    get_fills.add_argument("--status", type=web.BlockTradeStatus, action="append")
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    if args.command == "get-orders":
        client = AuthBitnomialHttpClient(
            connection_id=args.connection_id,
            auth_token=args.auth_token,
            base_url=args.base_url,
            env=args.env,
        )
        result = client.get_orders(
            symbols=args.symbols,
            product_ids=args.product_ids,
            product_types=args.product_types,
            clearing_firm_codes=args.clearing_firm_codes,
            account_ids=args.account_ids,
            connection_ids=args.connection_ids,
            day=args.day,
            limit=args.limit,
            begin_time=args.begin_time,
            end_time=args.end_time,
            order=args.order,
            cursor=args.cursor,
        )
        print(result)
    elif args.command == "get-fills":
        client = AuthBitnomialHttpClient(
            connection_id=args.connection_id,
            auth_token=args.auth_token,
            base_url=args.base_url,
            env=args.env,
        )
        result = client.get_fills(
            symbols=args.symbols,
            product_ids=args.product_ids,
            product_types=args.product_types,
            clearing_firm_codes=args.clearing_firm_codes,
            account_ids=args.account_ids,
            connection_ids=args.connection_ids,
            day=args.day,
            limit=args.limit,
            begin_time=args.begin_time,
            end_time=args.end_time,
            order=args.order,
            cursor=args.cursor,
        )
        print(result)
    elif args.command == "get-block-trades":
        client = AuthBitnomialHttpClient(
            connection_id=args.connection_id,
            auth_token=args.auth_token,
            base_url=args.base_url,
            env=args.env,
        )
        result = client.get_block_trades(
            symbols=args.symbols,
            product_ids=args.product_ids,
            product_types=args.product_types,
            clearing_firm_codes=args.clearing_firm_codes,
            account_ids=args.account_ids,
            connection_ids=args.connection_ids,
            status=args.status,
            day=args.day,
            limit=args.limit,
            begin_time=args.begin_time,
            end_time=args.end_time,
            order=args.order,
            cursor=args.cursor,
        )
        print(result)
    elif args.command == "get-product-spec":
        client = BitnomialHttpClient(base_url=args.base_url, env=args.env)
        result = client.get_product_spec(
            product_id=args.product_id,
            day=args.day,
            active=args.active,
            base_symbol=args.base_symbol,
        )
        print(result)

    elif args.command == "get-product-specs":
        client = BitnomialHttpClient(base_url=args.base_url, env=args.env)
        result = client.get_product_specs(
            day=args.day,
            active=args.active,
            base_symbol=args.base_symbol,
        )
        print(result)
    elif args.command == "get-product-datum":
        client = BitnomialHttpClient(args.base_url, args.env)
        result = client.get_product_datum(
            product_id=args.product_id,
            day=args.day,
            active=args.active,
            base_symbol=args.base_symbol,
        )
        print(result)
    elif args.command == "get-product-data":
        client = BitnomialHttpClient(args.base_url, args.env)
        result = client.get_product_data(
            day=args.day,
            active=args.active,
            base_symbol=args.base_symbol,
        )
        print(result)


if __name__ == "__main__":
    main()
