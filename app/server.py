import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from langchain_core.runnables import RunnableLambda
from langserve import add_routes


def base_path() -> str:
    """Normalised fleet prefix: '' or '/leading/no-trailing-slash'.

    nginx forwards the whole /direct/<agent>:<port> prefix UNCHANGED, so every
    route — including the docs — has to live under it. Empty => host root.
    """
    raw = (os.getenv("BASE_PATH") or "").strip().strip("/")
    return f"/{raw}" if raw else ""


BASE_PATH = base_path()

app = FastAPI(
    docs_url=f"{BASE_PATH}/docs",
    redoc_url=f"{BASE_PATH}/redoc",
    openapi_url=f"{BASE_PATH}/openapi.json",
)


@app.get(BASE_PATH or "/")
async def redirect_root_to_docs() -> RedirectResponse:
    return RedirectResponse(f"{BASE_PATH}/docs")


# A placeholder chain so the template BOOTS. The CLI generates
# `add_routes(app, NotImplemented)`, which raises before the server ever
# listens — replace this echo with your real chain.
echo_chain = RunnableLambda(lambda payload: {"echo": payload})

add_routes(app, echo_chain, path=f"{BASE_PATH}/echo")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
