from queue import Queue

import aiohttp
import uvicorn
from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every

app = FastAPI()
update_queue = Queue()


@app.post("/sendMessage")
async def new_update(update: dict):
    for i in range(10):
        update_queue.put(update)
        print(update)
    return {"message": "Update added to queue"}


@app.on_event("startup")
@repeat_every(seconds=1)
async def send_webhook() -> None:
    if not update_queue.empty():
        update = update_queue.get()
        print(f"GOT MESSAGE FROM QUEUE: {str(update)}")

        async with aiohttp.ClientSession() as session:
            response = await session.post("http://0.0.0.0:8001/webhook", json=update)
            print(f"RESPONSE: {await response.json()}")


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
