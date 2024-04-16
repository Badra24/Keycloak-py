from fastapi import FastAPI, Depends, HTTPException , status
from fastapi.responses import JSONResponse
from keycloak import KeycloakAuthenticationError, KeycloakOpenID , KeycloakAdmin
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.responses import RedirectResponse

from ErrorHandling.exceptions import (
    TokenRetrivalFailed,
    UrlInvalid,
    KeycloakError,
    TokenInvalid
)

app = FastAPI()

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

keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080/admin",
    realm_name="master",
    client_id="admin-cli",
    username="admin",
    password="admin",  
)

app.add_middleware(SessionMiddleware, secret_key="cEkusHWo67nU6PPpz0lhXjxNqrvLmmvo")

@app.get("/")
async def root(request: Request):
    return {"message": "Hello World"}

@app.get("/admin-getuser")
async def GetUser(request: Request, ):
    try:
        user_id = request.query_params.get('user_id')

        if not user_id :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="user not found")
        
        user_info = keycloak_admin.get_user(user_id=user_id)
        return JSONResponse(content=user_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

@app.post("/admin-createuser")
async def CreateUser(request: Request, payload: dict,):
    try:
                new_user_id = keycloak_admin.create_user(payload=payload)
                return JSONResponse(content={'user_id': new_user_id}) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/login")
async def login(request: Request):
    
    auth_url = keycloak_openid.auth_url(redirect_uri='http://localhost:8080')
    
    if not auth_url:
        
        raise UrlInvalid(
            status_code=status.HTTP_409_CONFLICT,
            reason=f"Invalid url: {auth_url}" 
        )
    print("auth_url:", auth_url)

    return RedirectResponse(auth_url)


@app.get("/callback")
async def callback(request: Request):
    try:
        username = request.query_params.get('username')
        password = request.query_params.get('password')
        

        token = keycloak_openid.token( username=username , password=password,
                                    redirect_uri='http://localhost:8080')

        request.session['token'] = token['access_token']
        
        return token
    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Keycloak authentication error: " + str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: " + str(e)
        )
@app.get("/protected")
async def protected(request: Request):
    token = request.session.get('token')

    if not token:
        raise TokenRetrivalFailed(
            status_code=status.HTTP_401_UNAUTHORIZED,
            reason="Toke Retrival Failed"
)

    return {"message": "Protected endpoint accessed successfully"}

@app.post("/register-client")
async def register_client(request: Request , payload: dict):
    
    token = request.session.get('token')
    
    if not token:
        raise TokenInvalid(
            status_code=status.HTTP_401_UNAUTHORIZED,
            reason="Access Token Invalid"
        )
    
    register = keycloak_openid.register_client(token=token, payload=payload)
    
    return register

@app.patch("/update-client")
async def update_client(request: Request, payload: dict):
    token = request.session.get('token')
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Invalid"
        )
        
    client_id = payload.get('clientId')
    
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID is required in the payload"
        )
        
    try:
        update_client_response = keycloak_openid.update_client(token=token, client_id=client_id, payload=payload)
        return update_client_response
    

    except KeycloakAuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Keycloak authentication error: " + str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error: " + str(e)
        )
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
    

    