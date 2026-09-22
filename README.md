# LangChain template

Provisioned from [`Qode-Platform/fleet-template-v1`](https://github.com/Qode-Platform/fleet-template-v1) — the fleet
lifecycle contract (`bin/`, `fleet.conf`, deploy workflows) with a
LangChain starter laid on top.

## Origin

    langchain app new (langchain-cli 0.0.37)

Generated 2026-09-21 on Node v22.12.0 / Python 3.12.3. **Dependencies were
never installed and this has never been built or run.** Boot it once before
trusting it.

## Fleet lifecycle

`fleet.conf` drives every script in `bin/`:

| step | command |
|---|---|
| install | `python3 -m venv .venv && .venv/bin/pip install --upgrade pip -r requirements.txt` |
| build | `(none)` |
| start | `.venv/bin/uvicorn app.server:app --host 0.0.0.0 --port $PORT` |

    ./bin/run       # install, build, start in the foreground
    ./bin/start     # start from existing build artifacts
    ./bin/restart   # rebuild and restart
    ./bin/stop      # stop whatever holds the port

Listens on `$PORT` (default `8000`); health check hits `/docs`.

## BASE_PATH

The fleet injects `BASE_PATH` (`/direct/<agent>:<port>`) and nginx forwards
that prefix **unchanged** — so this app serves every route and asset under
it. An empty or unset value means standalone mode: serve at the host root.

- Prefixed docs/openapi URLs, prefixed root redirect, and add_routes(path=BASE_PATH).
- `HEALTH_PATH` in `fleet.conf` stays un-prefixed; the fleet prepends `$BASE_PATH` itself.
- A value like `direct/x:3000/` is normalised to `/direct/x:3000`.
- Still will not boot until add_routes' NotImplemented is replaced with a real chain.

## What differs from stock output

- WILL NOT BOOT AS GENERATED: app/server.py calls add_routes(app, NotImplemented). Supply a chain first.
- Added requirements.txt mirroring the generated pyproject (poetry) so the fleet's pip-based install works.
- langchain-cli 0.0.37 still emits a LangServe app pinned to pydantic<2. Consider LangGraph for new work.

---

# langchain

## Installation

Install the LangChain CLI if you haven't yet

```bash
pip install -U langchain-cli
```

## Adding packages

```bash
# adding packages from
# https://github.com/langchain-ai/langchain/tree/master/templates
langchain app add $PROJECT_NAME

# adding custom GitHub repo packages
langchain app add --repo $OWNER/$REPO
# or with whole git string (supports other git providers):
# langchain app add git+https://github.com/hwchase17/chain-of-verification

# with a custom api mount point (defaults to `/{package_name}`)
langchain app add $PROJECT_NAME --api_path=/my/custom/path/rag
```

Note: you remove packages by their api path

```bash
langchain app remove my/custom/path/rag
```

## Setup LangSmith (Optional)

LangSmith will help us trace, monitor and debug LangChain applications.
You can sign up for LangSmith [here](https://smith.langchain.com/).
If you don't have access, you can skip this section

```shell
export LANGSMITH_TRACING=true
export LANGSMITH_API_KEY=<your-api-key>
export LANGSMITH_PROJECT=<your-project>  # if not specified, defaults to "default"
```

## Launch LangServe

```bash
langchain serve
```

## Running in Docker

This project folder includes a Dockerfile that allows you to easily build and host your LangServe app.

### Building the Image

To build the image, you simply:

```shell
docker build . -t my-langserve-app
```

If you tag your image with something other than `my-langserve-app`,
note it for use in the next step.

### Running the Image Locally

To run the image, you'll need to include any environment variables
necessary for your application.

In the below example, we inject the `OPENAI_API_KEY` environment
variable with the value set in my local environment
(`$OPENAI_API_KEY`)

We also expose port 8080 with the `-p 8080:8080` option.

```shell
docker run -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8080:8080 my-langserve-app
```

## Rule: everything under BASE_PATH

The fleet serves this app behind a proxy at `BASE_PATH=/direct/<agent>:<port>`, and the
prefix is forwarded **unchanged** — it is NOT stripped before it reaches the app. So every
route, every redirect, every asset URL and the docs/OpenAPI URLs must carry `$BASE_PATH`.

Never hard-code a leading-slash path in a redirect or a response.
`RedirectResponse("/docs")` and `add_routes(app, chain, path="/echo")` point at the
proxy's root and 404.

Use this template's own mechanism (FastAPI/LangServe):

- `app/server.py` defines `base_path()` and sets `docs_url`, `redoc_url` and
  `openapi_url` with the prefix; the root route and its redirect target are built from
  `BASE_PATH`.
- Every `add_routes(...)` call passes `path=f"{BASE_PATH}/<chain>"`. For a larger surface,
  hang the routes off a single `APIRouter(prefix=BASE_PATH)` instead of repeating the
  f-string.
- `HEALTH_PATH` in `fleet.conf` stays un-prefixed; the fleet prepends `$BASE_PATH` itself.
