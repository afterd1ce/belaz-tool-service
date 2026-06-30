from fastapi import FastAPI
from api.v1.auth import router as auth_router
from api.v1.instruments import router as instruments_router
from api.v1.movements import router as movements_router
from api.v1.calibration import router as calibration_router

app = FastAPI(title="BELAZ Tool Service")

app.include_router(auth_router)
app.include_router(instruments_router)
app.include_router(movements_router)
app.include_router(calibration_router)


@app.get("/")
def root():
    return {"service": "BELAZ Tool Service", "version": "1.0"}