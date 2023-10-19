import struct
from dataclasses import dataclass
from enum import Enum

from .core import BodyEncoding, MessageBody, MessageTypeBody


@dataclass
class LoginRequest(MessageBody):
    connection_id: int
    auth_token: bytes
    heartbeat_interval: int

    body_encoding = BodyEncoding.Login
    MSG_TYPE = b"L"
    FORMAT_STR = "<cQ32sB"

    def to_btp(self) -> bytes:
        return struct.pack(
            LoginRequest.FORMAT_STR,
            self.MSG_TYPE,
            self.connection_id,
            self.auth_token,
            self.heartbeat_interval,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "LoginRequest":
        message_type, connection_id, auth_token, heartbeat_interval = struct.unpack(
            LoginRequest.FORMAT_STR, data
        )
        assert message_type == LoginRequest.MSG_TYPE
        return LoginRequest(connection_id, auth_token, heartbeat_interval)


@dataclass
class LogoutRequest(MessageBody):
    persist_orders: str

    body_encoding = BodyEncoding.Login
    MSG_TYPE = b"K"
    FORMAT_STR = "<cc"

    def to_btp(self) -> bytes:
        return struct.pack(
            LogoutRequest.FORMAT_STR,
            self.MSG_TYPE,
            self.persist_orders.encode(),
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "LogoutRequest":
        message_type, persist_orders = struct.unpack(LogoutRequest.FORMAT_STR, data)
        assert message_type == LogoutRequest.MSG_TYPE
        return LogoutRequest(persist_orders.decode())


@dataclass
class LoginAck(MessageBody):
    body_encoding = BodyEncoding.Login
    MSG_TYPE = b"A"
    FORMAT_STR = "<c"

    def to_btp(self) -> bytes:
        return struct.pack(LoginAck.FORMAT_STR, self.MSG_TYPE)

    @classmethod
    def from_btp(cls, data: bytes) -> "LoginAck":
        (message_type,) = struct.unpack(LoginAck.FORMAT_STR, data)
        assert message_type == LoginAck.MSG_TYPE
        return LoginAck()


class LoginRejectReason(Enum):
    NoReqReceived = 0x01
    Unauthorized = 0x02
    AlreadyLoggedIn = 0x03


@dataclass
class LoginReject(MessageBody):
    reject_reason: LoginRejectReason

    body_encoding = BodyEncoding.Login
    MSG_TYPE = b"R"
    FORMAT_STR = "<cB"

    def to_btp(self) -> bytes:
        return struct.pack(
            LoginReject.FORMAT_STR,
            self.MSG_TYPE,
            self.reject_reason.value,
        )

    @classmethod
    def from_btp(cls, data: bytes) -> "LoginReject":
        message_type, reject_reason = struct.unpack(LoginReject.FORMAT_STR, data)
        assert message_type == LoginReject.MSG_TYPE
        return LoginReject(LoginRejectReason(reject_reason))


class Login(MessageTypeBody):
    body_encoding = BodyEncoding.Login

    MESSAGE_TYPES = {
        LoginRequest.MSG_TYPE: LoginRequest.from_btp,
        LogoutRequest.MSG_TYPE: LogoutRequest.from_btp,
        LoginAck.MSG_TYPE: LoginAck.from_btp,
        LoginReject.MSG_TYPE: LoginReject.from_btp,
    }
