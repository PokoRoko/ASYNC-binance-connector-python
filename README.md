# Binance Public API Connector Python
[![Python version](https://img.shields.io/pypi/pyversions/binance-connector)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code_style-black-black)](https://black.readthedocs.io/en/stable/)


This is a lightweight library that works as a ASYNC connector to [Binance public API](https://github.com/binance/binance-spot-api-docs)

- Supported APIs:
    - `/api/*`
    - `/sapi/*`
    - Spot Websocket Market Stream
    - Spot User Data Stream
- Inclusion of test cases and examples
- Customizable base URL, request timeout and HTTP proxy
- Response metadata can be displayed

## ToDo:  

- async websocket
- proxy
- 
## Installation

```bash
git clone git@github.com:PokoRoko/ASYNC-binance-connector-python.git
```

## RESTful APIs

Usage examples:
```python
import asyncio
import os
from binance.spot import Spot

api_key = "<API_KEY>"
api_secret = "<API_SECRET>"


async def main():
    key = os.getenv("API_KEY")
    secret = os.getenv("API_SECRET")

    spot_client = Spot(key=key, secret=secret)
    res = await spot_client.account_snapshot("SPOT")
    print(res)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
```
### !!! Outdated information !!!  
Please find `examples` folder to check for more endpoints. 


### Base URL

If `base_url` is not provided, it defaults to `api.binance.com`.<br/>
It's recommended to pass in the `base_url` parameter, even in production as Binance provides alternative URLs
in case of performance issues:
- `https://api1.binance.com`
- `https://api2.binance.com`
- `https://api3.binance.com`

### Optional parameters

PEP8 suggests _lowercase with words separated by underscores_, but for this connector,
the methods' optional parameters should follow their exact naming as in the API documentation.

### RecvWindow parameter

Additional parameter `recvWindow` is available for endpoints requiring signature.<br/>
It defaults to `5000` (milliseconds) and can be any value lower than `60000`(milliseconds).
Anything beyond the limit will result in an error response from Binance server.

```python
from binance.spot import Spot as Client

client = Client(key, secret)
response = client.get_order('BTCUSDT', orderId=11, recvWindow=10000)
```

### Timeout

`timeout` is available to be assigned with the number of seconds you find most appropriate to wait for a server response.<br/>
Please remember the value as it won't be shown in error message _no bytes have been received on the underlying socket for timeout seconds_.<br/>
By default, `timeout` is None. Hence, requests do not time out.

```python
from binance.spot import Spot as Client

client= Client(timeout=1)
```

### Proxy

NOW Proxy not is supported.

```python
from binance.spot import Spot as Client

proxies = { 'https': 'http://1.2.3.4:8080' }

client= Client(proxies=proxies)
```


### Response Metadata

The Binance API server provides weight usages in the headers of each response.
You can display them by initializing the client with `show_limit_usage=True`:

```python
from binance.spot import Spot as Client

client = Client(show_limit_usage=True)
print(client.time())
```
returns:

```python
{'data': {'serverTime': 1587990847650}, 'limit_usage': {'x-mbx-used-weight': '31', 'x-mbx-used-weight-1m': '31'}}
```
You can also display full response metadata to help in debugging:

```python
client = Client(show_header=True)
print(client.time())
```

returns:

```python
{'data': {'serverTime': 1587990847650}, 'header': {'Context-Type': 'application/json;charset=utf-8', ...}}
```

If `ClientError` is received, it'll display full response meta information.

### Display logs

Setting the log level to `DEBUG` will log the request URL, payload and response text.

### Error

There are 2 types of error returned from the library:
- `binance.error.ClientError`
    - This is thrown when server returns `4XX`, it's an issue from client side.
    - It has 4 properties:
        - `status_code` - HTTP status code
        - `error_code` - Server's error code, e.g. `-1102`
        - `error_message` - Server's error message, e.g. `Unknown order sent.`
        - `header` - Full response header. 
- `binance.error.ServerError`
    - This is thrown when server returns `5XX`, it's an issue from server side.

## Websocket

```python
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient

def message_handler(message):
    print(message)

ws_client = WebsocketClient()
ws_client.start()

ws_client.mini_ticker(
    symbol='bnbusdt',
    id=1,
    callback=message_handler,
)

# Combine selected streams
ws_client.instant_subscribe(
    stream=['bnbusdt@bookTicker', 'ethusdt@bookTicker'],
    callback=message_handler,
)

ws_client.stop()
```
More websocket examples are available in the `examples` folder

### Heartbeat

Once connected, the websocket server sends a ping frame every 3 minutes and requires a response pong frame back within
a 10 minutes period. This package handles the pong responses automatically.

### Testnet

```python
from binance.websocket.spot.websocket_client import SpotWebsocketClient as WebsocketClient

ws_client = WebsocketClient(stream_url='wss://testnet.binance.vision')
```

## Test Case
Now test dont work in fork. ToDo
```python
# In case packages are not installed yet
pip install -r requirements/requirements-test.txt

pytest
```

## Limitation

Futures and Vanilla Options APIs are not supported:
  - `/fapi/*`
  - `/dapi/*`
  - `/vapi/*`
  -  Associated Websocket Market and User Data Streams

## Contributing

Contributions are welcome.<br/>
If you've found a bug within this project, please open an issue to discuss what you would like to change.<br/>
If it's an issue with the API, please open a topic at [Binance Developer Community](https://dev.binance.vision)
