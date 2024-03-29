import asyncio
import random
from typing import Annotated

from fastapi import FastAPI, Path
from sse_starlette import EventSourceResponse
from starlette.requests import Request
import math
from itertools import count
import uvicorn
import logging

logging.basicConfig(
    filename="resources.log",
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
app = FastAPI()

BASE_PRICE = 100


def generate_spike_price(
    step, noise_level=0.5, trend=0.1, spike_frequency=5, amplitude=10
):
    if step % spike_frequency == 0:
        spike = random.choice([-amplitude, amplitude]) * random.random()
    else:
        spike = 0
    noise = random.uniform(-noise_level, noise_level)
    return round(BASE_PRICE + trend * step + spike + noise)


def generate_sinusoidal_price(step, noise_level=0.5, period=40, amplitude=10):
    sinusoidal_price = amplitude * math.sin(2 * math.pi * step / period) + BASE_PRICE
    noise = random.uniform(-noise_level, noise_level)
    return round(sinusoidal_price + noise, 2)


def generate_sawtooth_price(step, amplitude=10):
    direction = 1 if step % 2 == 0 else -1
    spike = random.random() * amplitude * direction
    return round(BASE_PRICE + spike)


price_generators = {
    "sinusoidal": generate_sinusoidal_price,
    "spiky": generate_spike_price,
    "sawtooth": generate_sawtooth_price,
}


@app.get("/prices_stream/{asset_name}")
async def prices_stream(
    request: Request,
    asset_name: Annotated[str, Path(pattern="sinusoidal|spiky|sawtooth")],
) -> EventSourceResponse:
    async def price_generator():
        for step in count():
            if await request.is_disconnected():
                logging.info("Request disconnected")
                break
            price = price_generators[asset_name](step)
            yield {
                "event": f"new_price",
                "data": f"{price}",
            }
            await asyncio.sleep(1)

    return EventSourceResponse(price_generator())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
