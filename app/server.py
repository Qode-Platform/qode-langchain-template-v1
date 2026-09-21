import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
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


# Edit this to add the chain you want to add. Keep BASE_PATH on the front of
# whatever path you mount it at, or the ingress will not reach it.
add_routes(app, NotImplemented, path=BASE_PATH or "")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
