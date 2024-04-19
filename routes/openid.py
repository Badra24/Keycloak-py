from tkinter.tix import Form
from fastapi import  Body,APIRouter, Depends, HTTPException , status
from fastapi.responses import JSONResponse
from jose import JWTError
import jwt
from keycloak.keycloak_openid import KeycloakOpenID
import keycloak
import keycloak.keycloak_openid
from openai import BaseModel
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi import Query

import jwt
from ErrorHandling.exceptions import (
    TokenRetrivalFailed,
    UrlInvalid,
    KeycloakError,
    TokenInvalid
)

router = APIRouter()

# Konfigurasi Keycloak
# keycloak_openid = KeycloakOpenID(
#     server_url="http://keycloak:8080/auth/",
#     realm_name="your_realm",
#     client_id="your_client_id",
#     client_secret_key="your_client_secret_key",
# )


keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8080/admin",
    realm_name="master",
    client_id="client_id",
    client_secret_key="cEkusHWo67nU6PPpz0lhXjxNqrvLmmvo",
)
# ALGORITHM = "RS256"

# class TokenPayload(BaseModel):
#     iat: str
#     exp: str

# def read_token_info(token: str):
#     try:
#         payload = jwt.decode(token , keycloak_openid.client_secret_key , algorithms=[ALGORITHM])
#         return TokenPayload(**payload)
#     except JWTError as e:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
    

@router.post("/userInfo")
async def userInfo(request: Request):
    try:
        token = request.headers.get("Authorization")
        if token:
            token = token.replace("Bearer ", "")
            userInfo = keycloak_openid.userinfo(token=token)
            # token_info = read_token_info(token)
            return {'user_info': userInfo}
            # return {"userInfo": userInfo, "tokenInfo": token_info}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No token provided")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


    
@router.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@router.post("/login")
async def login(username: str = Body(...), password: str = Body(...)):
    try:
        token = keycloak_openid.token(username=username, password=password, grant_type="password")
        if token:
            return JSONResponse(content={"access_token" : token["access_token"] ,
                                        "refresh_token" : token["refresh_token"]
                                        ,"token_type" : token["token_type"]})
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
        


@router.get("/callback")
async def callback(request: Request  ):
    try:
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        
        token = keycloak_openid.token( username=username , password=password,
                                    redirect_uri='http://localhost:8080')

        request.session['token'] = token['access_token']
    
        return RedirectResponse(token)
    except keycloak.exceptions.KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Keycloak authentication error: " + str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: " + str(e)
        )
        
        
@router.get("/protected")
async def protected(request: Request):
    token = request.session.get('token')

    if not token:
        raise TokenRetrivalFailed(
            status_code=status.HTTP_401_UNAUTHORIZED,
            reason="Toke Retrival Failed"
)

    return {"message": "Protected endpoint accessed successfully"}

@router.post("/register-client")
async def register_client(request: Request , payload: dict):
    
    token = request.session.get('token')
    
    if not token:
        raise TokenInvalid(
            status_code=status.HTTP_401_UNAUTHORIZED,
            reason="Access Token Invalid"
        )
    
    register = keycloak_openid.register_client(token=token, payload=payload)
    
    return RedirectResponse(register)


    
