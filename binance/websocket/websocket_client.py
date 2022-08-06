import asyncio
import json
import logging
import websockets


class BinanceWebsocketClient:
    def __init__(self, stream_url):
        self._logger = logging.getLogger(__name__)
        self._subscriptions = {}

        self._stream_url = stream_url

    def _single_stream(self, stream):
        if isinstance(stream, str):
            return True
        elif isinstance(stream, list):
            return False
        else:
            raise ValueError(f"Invalid stream name {type(stream)}= {stream}")

    async def _start_subscribe(self, id, stream_name, payload, callback, is_combined=False, is_live=True):
        if stream_name in self._subscriptions:
            self._logger.error(f"Stream already exist {stream_name=} url={self._stream_url}")
            return False

        if is_combined:
            url = self._stream_url + "/stream"
        else:
            url = self._stream_url + "/ws"

        payload_obj = json.loads(payload.decode("utf8"))
        if not is_live:
            if is_combined:
                url = url + "?streams=" + payload_obj["params"][0]
            else:
                url = url + "/" + payload_obj["params"][0]
            payload_obj = {}

        websocket = await websockets.connect(url)
        await websocket.send(json.dumps(payload_obj))

        stop_event = asyncio.Event()
        self._subscriptions[id] = stop_event
        self._logger.info("Connection with URL: {}".format(url))

        while not stop_event.is_set():
            try:
                rec = await asyncio.wait_for(websocket.recv(), timeout=1)
                callback(rec)
            except:
                continue
        await websocket.close()
        logging.info(f"Subscription {id=} {stream_name=} ended")

    async def live_subscribe(self, stream, id, callback, **kwargs):
        """
        live subscribe websocket
        Connect to the server
        - SPOT: wss://stream.binance.com:9443/ws
        - SPOT testnet : wss://testnet.binance.vision/ws

        and sending the subscribe message, e.g.
        {"method": "SUBSCRIBE","params":["btcusdt@miniTicker"],"id": 100}
        """
        combined = False
        if self._single_stream(stream):
            stream = [stream]
        else:
            combined = True

        data = {"method": "SUBSCRIBE", "params": stream, "id": id}

        data.update(**kwargs)
        payload = json.dumps(data, ensure_ascii=False).encode("utf8")
        stream_name = "-".join(stream)
        await self._start_subscribe(id, stream_name, payload, callback, is_combined=combined, is_live=True)

    async def instant_subscribe(self, stream, callback, **kwargs):
        """Instant subscribe, e.g.
        wss://stream.binance.com:9443/ws/btcusdt@bookTicker
        wss://stream.binance.com:9443/stream?streams=btcusdt@bookTicker/bnbusdt@bookTicker

        """
        combined = False
        if not self._single_stream(stream):
            combined = True
            stream = "/".join(stream)

        data = {"method": "SUBSCRIBE", "params": stream}

        data.update(**kwargs)
        payload = json.dumps(data, ensure_ascii=False).encode("utf8")
        stream_name = "-".join(stream)
        await self._start_subscribe(id, stream_name, payload, callback, is_combined=combined, is_live=False)

    async def stop_by_id(self, id):
        self._logger.debug("Stopped subscribe from stop event")
        stop_event = self._subscriptions.get(id)
        if stop_event:
            stop_event.set()
        else:
            self._logger.error(f"There is no such id '{id}' in subscriptions")

    async def stop_all(self):
        for stop_events in self._subscriptions.values():
            await stop_events.set()
        logging.info(f"All subscribe stopped - ids: {list(self._subscriptions.keys())}")

