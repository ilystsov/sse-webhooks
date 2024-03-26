from http import HTTPStatus

import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.post("/webhook")
async def webhook(update: dict):
    print(update)

    return HTTPStatus.OK, str(update)


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8001)
