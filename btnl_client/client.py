import asyncio
import time

from btnl_client.protocol import (
    BodyEncoding,
    Heartbeat,
    LoginAck,
    LoginRequest,
    Message,
    Open,
    Side,
    TimeInForce,
    new_message,
)


class OrderEntryClient:
    HEARTBEAT_INTERVAL = 30

    def __init__(self, host, port, connection_id, hex_auth_token):
        assert len(hex_auth_token) == 64
        self.host = host
        self.port = port
        self.connection_id = connection_id
        self.auth_token = bytes.fromhex(hex_auth_token)
        self.last_sent_msg_time = 0
        self.sequence_id = 1

    async def trade(self):
        # Implement handling of outgoing messages here
        pass

    async def app_message(self, message):
        # Implement handling of incoming messages here
        print(f"App message: {message}")
        pass

    def reset_heartbeat_timer(self):
        self.last_sent_msg_time = time.time()

    async def login(self):
        # Create login request message
        login_request = LoginRequest(
            self.connection_id,
            self.auth_token,
            heartbeat_interval=self.HEARTBEAT_INTERVAL,  # heartbeat interval
        )

        # Send login request
        await self.send_message(login_request)

        login_resp = await Message.read_message(self.reader)
        print(login_resp)
        if not isinstance(login_resp.body, LoginAck):
            raise ValueError(f"Bad login response: {login_resp}")
        return login_resp

    async def send_message(self, msg_body):
        seq_id = self.sequence_id
        if msg_body.body_encoding == BodyEncoding.Heartbeat:
            seq_id = 0
        else:
            self.sequence_id += 1
        msg = new_message(seq_id, msg_body).to_btp()
        # Write message to socket
        self.reset_heartbeat_timer()
        self.writer.write(msg)

    async def handle_btp_message(self, message):
        # TODO make a heartbeat receive timer
        if isinstance(message.body, Heartbeat):
            return
        await self.app_message(message)

    async def run(self):
        # Establish connection
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        # Login
        await self.login()
        # Handle incoming msgs, trade, and heartbeat concurrently
        await asyncio.gather(
            self.receive_messages_loop(), self.trade_loop(), self.heartbeat_loop()
        )

    async def receive_messages_loop(self):
        while True:
            message = await Message.read_message(self.reader)
            await self.handle_btp_message(message)

    async def heartbeat_loop(self):
        while True:
            # Check if it's time to send a heartbeat
            if time.time() - self.last_sent_msg_time > self.HEARTBEAT_INTERVAL:
                # It's been more than 30s since the last heartbeat
                self.reset_heartbeat_timer()
                await self.send_message(Heartbeat())

            # Sleep for a bit to prevent this loop from running too fast
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def trade_loop(self):
        """
        This is a bit silly, but works well for basic testing
        """
        while True:
            await self.trade()
            # Sleep for a bit to prevent this loop from running too fast
            await asyncio.sleep(1)

    def stop(self):
        # Close the connection
        self.writer.close()


# Testing
# order = Open(123, 456, Side.Bid, 789, 10, TimeInForce.Day)
# msg = Message(1, order)
# print(order.to_btp())
# print(msg.to_btp())
# print(order.to_btp().hex())
# print(msg.to_btp().hex())

# print(Message.from_btp(Message(0, Heartbeat()).to_btp()))

# parsed_msg = Message.from_btp(msg.to_btp())
# print(parsed_msg)


# Usage:
# client = SimpleTrader(
#     "localhost",
#     11000,
#     1,
#     "0000000000000000000000000000000000000000000000000000000000000001",
# )
# asyncio.run(client.run())

# TODO move into example folder
# class SimpleTrader(OrderEntryClient):
#     order_id = 0
#     async def trade(self):
#         self.order_id += 1
#         await self.send_message(
#             Open(self.order_id, 3668, Side.Bid, 10000, 10, TimeInForce.Day)
#         )
