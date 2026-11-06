from contextlib import asynccontextmanager
import os

from fastapi import FastAPI


from checkout_commerce.infra.database import create_tables
from checkout_commerce.client_manager import client_manager

from checkout_commerce.checkout.router import router as checkout_router


from prometheus_fastapi_instrumentator import Instrumentator





@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    await create_tables()
    await client_manager.startup()

    yield

    await client_manager.shutdown()
    # Perform any shutdown tasks here



app = FastAPI(
    title="Checkout Commerce",
    version="1.0.0",
    lifespan=lifespan
)


app.include_router(checkout_router)

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

@app.get("/health")
async def health_check():
    payment_url = os.getenv("PAYMENT_SERVICE_URL")
    return {"status": payment_url}





if __name__ == "__main__":
    import uvicorn

    port = os.getenv("PORT", 8005)
    host = os.getenv("HOST", "0.0.0.0")


    uvicorn.run(app, host=host, port=port, reload=True)