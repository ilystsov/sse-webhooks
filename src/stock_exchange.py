import functools
import os
from queue import Queue
from dotenv import load_dotenv
import sys
import uvicorn
from fastapi import FastAPI
from sseclient import SSEClient
import asyncio
from collections import defaultdict
from fastapi_utils.tasks import repeat_every
import aiohttp

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.contracts import TradeRequest, TradeResponse
import logging

logging.basicConfig(
    filename="stock_exchange.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()
PRICES_STREAM_URL = os.getenv("PRICES_STREAM_URL")
app = FastAPI()


assets_prices: defaultdict[str, Queue] = defaultdict(lambda: Queue())
webhooks_for_assets: dict[str, list[str]] = {
    "sinusoidal": [os.getenv("BULL_WEBHOOK_URL"), os.getenv("BEAR_WEBHOOK_URL")],
    "spiky": [os.getenv("BEAR_WEBHOOK_URL")],
    "sawtooth": [os.getenv("BULL_WEBHOOK_URL")],
}


def update_asset_price_from_source(base_url: str, asset_name: str):
    events = SSEClient(base_url + "/" + asset_name)
    for event in events:
        try:
            new_price = float(event.data)
            assets_prices[asset_name].put(new_price)
            logging.info(f"Updated {asset_name} price to {new_price}")
        except ValueError:
            logging.error(f"Invalid data for {asset_name}: {event.data}")


async def start_price_updates():
    base_url = PRICES_STREAM_URL
    asset_names = [
        "sinusoidal",
        "spiky",
        "sawtooth",
    ]
    loop = asyncio.get_running_loop()
    tasks = []
    for asset_name in asset_names:
        task = loop.run_in_executor(
            None,
            functools.partial(
                update_asset_price_from_source, base_url=base_url, asset_name=asset_name
            ),
        )
        tasks.append(task)
    await asyncio.gather(*tasks)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_price_updates())


@app.on_event("startup")
@repeat_every(seconds=0.5)
async def send_webhook() -> None:
    for asset_name, webhook_list in webhooks_for_assets.items():
        if not assets_prices[asset_name].empty() and webhook_list:
            price = assets_prices[asset_name].get()
            asset_info = {"asset_name": asset_name, "price": price}
            for webhook_url in webhook_list:
                async with aiohttp.ClientSession() as session:
                    response = await session.post(webhook_url, json=asset_info)
                    logging.info(
                        f"Sent webhook to {webhook_url} with response: {await response.json()}"
                    )


@app.post("/buy_asset")
async def buy_asset(request: TradeRequest) -> TradeResponse:
    logging.info(
        f"Asset {request.asset_name} bought by {request.buyer_name} at {request.price}"
    )
    return TradeResponse(success=True)


@app.post("/sell_asset")
async def sell_asset(request: TradeRequest) -> TradeResponse:
    logging.info(
        f"Asset {request.asset_name} sold by {request.buyer_name} at {request.price}"
    )
    return TradeResponse(success=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)
