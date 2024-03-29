from pydantic import BaseModel


class TradeRequest(BaseModel):
    asset_name: str
    buyer_name: str
    price: float


class TradeResponse(BaseModel):
    success: bool
