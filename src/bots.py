import os
from http import HTTPStatus
from dotenv import load_dotenv
import aiohttp
import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import JSONResponse
import logging

logging.basicConfig(
    filename="bots.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

load_dotenv()

app = FastAPI()
old_prices_bull: dict[str, float] = {}
old_prices_bear: dict[str, float] = {}
purchase_prices: dict[str, float] = {}

STOCK_EXCHANGE_URL = os.getenv("STOCK_EXCHANGE_URL")
SELL_THRESHOLD = -0.1


@app.post("/bull/webhook")
async def bull_webhook(request: Request):
    data = await request.json()
    asset_name, new_price = data["asset_name"], data["price"]
    old_price = old_prices_bull.get(asset_name, None)

    if old_price is not None:
        if new_price > old_price:
            await sell_asset(asset_name, "bull", new_price)
        elif new_price < old_price:
            await buy_asset(asset_name, "bull", new_price)
    old_prices_bull[asset_name] = new_price
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "success"})


@app.post("/bear/webhook")
async def bear_webhook(request: Request):
    data = await request.json()

    asset_name, new_price = data["asset_name"], data["price"]
    purchase_price = purchase_prices.get(asset_name, None)
    old_price = old_prices_bear.get(asset_name, None)

    if old_price is not None:
        price_change = (new_price - old_price) / old_price
        if price_change < SELL_THRESHOLD:
            await sell_asset(asset_name, "bear", new_price)
    if purchase_price is None or new_price < purchase_price:
        await buy_asset(asset_name, "bear", new_price)
        purchase_prices[asset_name] = new_price

    old_prices_bear[asset_name] = new_price
    return JSONResponse(status_code=HTTPStatus.OK, content={"message": "success"})


async def buy_asset(asset_name, buyer_name, price):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{STOCK_EXCHANGE_URL}/buy_asset",
            json={
                "asset_name": asset_name,
                "buyer_name": buyer_name,
                "price": price,
            },
        )
    logging.info(f"{buyer_name} buys {asset_name} at {price}")


async def sell_asset(asset_name, buyer_name, price):
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"{STOCK_EXCHANGE_URL}/sell_asset",
            json={
                "asset_name": asset_name,
                "buyer_name": buyer_name,
                "price": price,
            },
        )
    logging.info(f"{buyer_name} sells {asset_name} at {price}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
