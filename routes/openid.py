from fastapi import  APIRouter, Depends, HTTPException , status
from fastapi.responses import JSONResponse
from keycloak.keycloak_openid import KeycloakOpenID
import keycloak
import keycloak.keycloak_openid
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse
from fastapi import Query

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



@router.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@router.get("/login")
async def login():
    
    auth_url = keycloak_openid.auth_url(redirect_uri='http://localhost:8080')
    
    if not auth_url:
        
        raise UrlInvalid(
            status_code=status.HTTP_409_CONFLICT,
            reason=f"Invalid url: {auth_url}"
        )
    print("auth_url:", auth_url)

    return RedirectResponse(auth_url)


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


    
