import pytest
from httpx import AsyncClient, ASGITransport
from src.stock_exchange import app


@pytest.mark.asyncio
async def test_buy_asset():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/buy_asset",
            json={
                "asset_name": "test_asset",
                "buyer_name": "test_buyer",
                "price": 100,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_sell_asset():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/sell_asset",
            json={
                "asset_name": "test_asset",
                "buyer_name": "test_seller",
                "price": 100,
            },
        )
        assert response.status_code == 200
        assert response.json()["success"] is True
