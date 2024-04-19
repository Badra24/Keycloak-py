from fastapi import FastAPI, HTTPException , status
from starlette.middleware.sessions import SessionMiddleware

from routes import admin, openid
import logging
import sys
from fastapi.middleware.cors import CORSMiddleware




app=FastAPI()

origins = [
    "*"
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)

logger.info('API is starting up')
app.add_middleware(SessionMiddleware, secret_key="cEkusHWo67nU6PPpz0lhXjxNqrvLmmvo")

app.include_router(admin.router , prefix="/surrounding/v1/admin")
app.include_router(openid.router ,  prefix="/surrounding/v1/openid")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, 
                host="0.0.0.0",
                port=8000, 
                reload=True)