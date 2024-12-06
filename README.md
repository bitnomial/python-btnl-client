# Python Bitnomial Client

This is a basic python SDK for Bitnomial's trading interface.

[Documentation](https://bitnomial.com/docs)

## Development

Setup a [virtualenv](https://virtualenv.pypa.io/en/latest/user_guide.html) either manually or with
[direnv](https://direnv.net/man/direnv-stdlib.1.html#codelayout-python-ltpythonexegtcode).

Once you have a python virtualenv install dependencies with `pip install .`. If your editor supports
language servers consider using [pyright](https://github.com/microsoft/pyright).

## Usage

The modules can be imported and used as a library. Particular modules that users might start with
are
 - `btnl_client.client`: Order entry protocol client, see
   [btnl_client/client.py](btnl_client/client.py) for example code
 - `btnl_client.websocket`: Websocket protocol client, see
   [btnl_client/websocket.py](btnl_client/websocket.py) for example code
 - `btnl_client.product`: HTTP API client, see [btnl_client/product.py](btnl_client/product.py) for
   example code

In addition to the example code in each of these modules the library has a CLI tool for interactive
usage and testing. This interface is likely to change between versions, so it's not recommended to
build applications against it. Some example commands are shown below

Setup a default websocket feed and print events as they occur

``` sh
$ python -m btnl_client ws-feed
```

Query orders for a given connection ID

```sh
$ python -m btnl_client get-orders <connection_id> <auth_token>
```

Query fills for a given connection ID 

```sh
$ python -m btnl_client get-fills <connection_id> <auth_token>
```

Query active product specs

```sh
$ python -m btnl_client get-product-specs --active 
```

Query product spec for a specific product 

```sh
$ python -m btnl_client get-product-spec <product_id>
```

For extended information usage, including a full list of commands and their options and flags, use
the `--help` flag
