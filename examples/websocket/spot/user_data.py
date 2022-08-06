#!/usr/bin/env python

import asyncio
import os
import logging
from binance.lib.utils import config_logging
from binance.spot import Spot
from binance.websocket.spot.websocket_client import SpotWebsocketClient

config_logging(logging, logging.DEBUG)


def message_handler(message):
    print(message)


async def user_data(ws_client, id):
    key = os.getenv("<API_KEY>")
    secret = "<API_SECRET>"
    client = Spot(key=key,
                  secret=secret,
                  # base_url="https://testnet.binance.vision"
                  )

    listen_key = await client.new_listen_key()
    await client.session.close()

    try:
        logging.info(f"Receiving listen key : {listen_key['listenKey']}")
    except KeyError:
        logging.error(f"Error get listen key : {listen_key}")
        return

    await ws_client.user_data(
        listen_key=listen_key["listenKey"],
        id=id,
        callback=message_handler,
    )


async def test_stop_event(ws_client, id):
    for i in range(7):
        print(i)
        await asyncio.sleep(1)
        await ws_client.stop_by_id(id)


async def main():
    id = 1
    ws_client = SpotWebsocketClient()
    await asyncio.gather(test_stop_event(ws_client, id), user_data(ws_client, id))


loop = asyncio.new_event_loop()
loop.run_until_complete(main())