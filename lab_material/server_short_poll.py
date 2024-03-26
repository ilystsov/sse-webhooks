from queue import Queue

import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()
update_queue = Queue()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/getUpdates")
async def get_updates():
    return update_queue.get() if not update_queue.empty() else {}


@app.post("/sendMessage")
async def new_update(update: dict):
    update_queue.put(update)
    print(update)
    return {"message": "Update added to queue"}


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
