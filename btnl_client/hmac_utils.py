#!/usr/bin/env python3
import hmac
import hashlib
from typing import Dict, Union, List, Optional
from base64 import b64encode


CONNECTION_ID_HEADER = "BTNL-CONNECTION-ID"
TIMESTAMP_HEADER = "BTNL-AUTH-TIMESTAMP"
SIGNATURE_HEADER = "BTNL-SIGNATURE"


def params_string(params: Dict[str, Optional[Union[List[str], str]]]) -> str:
    def to_qstr(k, v) -> Optional[str]:
        if v is None:
            return None
        elif v is list:
            return sep.join(map(lambda x: k + "=" + str(x), filter(None, v)))
        else:
            return k + "=" + str(v)

    sep: str = "?"
    parts = filter(None, map(lambda x: to_qstr(*x), params.items()))
    return sep + sep.join(parts)


def signature(
    method: str,
    path: str,
    params: Dict[str, Union[None, str, List[str]]],
    timestamp: str,
    connection_id: int,
    auth_token: str,
) -> str:
    msg = (
        method
        + path
        + params_string(params)
        + TIMESTAMP_HEADER
        + timestamp
        + CONNECTION_ID_HEADER
        + str(connection_id)
    )
    hashed = hmac.new(
        bytes(auth_token, "utf-8"),
        msg=bytes(msg, "utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    return b64encode(hashed).decode()
