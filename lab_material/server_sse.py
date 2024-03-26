import asyncio
import time
from queue import Queue

import uvicorn
from fastapi import FastAPI
from sse_starlette import EventSourceResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request

app = FastAPI()
update_queue = Queue()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/stream")
async def message_stream(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                print("Request disconnected")
                break

            if not update_queue.empty():
                update = update_queue.get()
                print(f"GOT MESSAGE FROM QUEUE: {str(update)}")

                yield {
                    "event": "new_message",
                    "id": "message_id",
                    "data": update["message"],
                }
            else:
                yield {
                    "event": "end_event",
                    "id": "message_id",
                    "data": "End of the stream",
                }

    return EventSourceResponse(event_generator())


@app.post("/sendMessage")
async def new_update(update: dict):
    for i in range(10):
        update_queue.put(update)
        print(update)
    return {"message": "Update added to queue"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
