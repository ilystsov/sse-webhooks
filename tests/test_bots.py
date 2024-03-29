import os

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from src.bots import app, old_prices_bear, purchase_prices
from src.bots import old_prices_bull
from dotenv import load_dotenv


load_dotenv()
STOCK_EXCHANGE_URL = os.getenv("STOCK_EXCHANGE_URL")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_price,new_price,expected_action",
    [
        (120, 110, "buy_asset"),
        (100, 110, "sell_asset"),
    ],
)
async def test_bull_bot_actions(initial_price, new_price, expected_action):
    asset_name = "test_asset"
    old_prices_bull[asset_name] = initial_price

    data = {"asset_name": asset_name, "price": new_price}

    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status = 200
        mock_post.return_value.json.return_value = {"success": True}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.post("/bull/webhook", json=data)
            mock_post.assert_called_with(
                f"{STOCK_EXCHANGE_URL}/{expected_action}",
                json={
                    "asset_name": asset_name,
                    "buyer_name": "bull",
                    "price": new_price,
                },
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "initial_price,last_purchase_price,new_price,expected_action",
    [
        (120, 120, 105, "buy_asset"),
        (120, 80, 90, "sell_asset"),
    ],
)
async def test_bear_bot_actions(
    initial_price, last_purchase_price, new_price, expected_action
):
    asset_name = "test_asset"
    old_prices_bear[asset_name] = initial_price
    purchase_prices[asset_name] = last_purchase_price

    data = {"asset_name": asset_name, "price": new_price}

    with patch("aiohttp.ClientSession.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.status = 200
        mock_post.return_value.json.return_value = {"success": True}

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as ac:
            await ac.post("/bear/webhook", json=data)

            mock_post.assert_called_with(
                f"{STOCK_EXCHANGE_URL}/{expected_action}",
                json={
                    "asset_name": asset_name,
                    "buyer_name": "bear",
                    "price": new_price,
                },
            )
