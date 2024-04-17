from fastapi import APIRouter , FastAPI, Depends, HTTPException , status
from fastapi.responses import JSONResponse, RedirectResponse
from keycloak.keycloak_admin import KeycloakAdmin
import keycloak
import keycloak.exceptions
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from fastapi import Query

from ErrorHandling.exceptions import (
    TokenRetrivalFailed,
    UrlInvalid,
    KeycloakError,
    TokenInvalid
)

router = APIRouter()




keycloak_admin = KeycloakAdmin(
    server_url="http://localhost:8080/admin",
    realm_name="master",
    client_id="admin-cli",
    username="admin",
    password="admin",  
)


@router.get("/")
async def root(request: Request):
    return {"message": "Hello World"}


@router.get("/get-realm")
async def getRealmByName():
    try:
        realm_data = keycloak_admin.get_realms()
        return JSONResponse(content=realm_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

@router.get("/get-realm-byName")
async def getRealmByName(request: Request):
    try:
        real_name = request.query_params.get("real_name")
        realm_data = keycloak_admin.get_realm(realm_name=real_name)
        return JSONResponse(content=realm_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    
@router.post("/create-realm")
async def createRealm(payload : dict):
    try:
        existing_realm = keycloak_admin.get_realm(payload["realm"])
        if existing_realm:
           
            return JSONResponse(content={"detail": "Realm already exists."}, status_code=409)

        # Realm belum ada, maka buat realm baru
        new_realm = keycloak_admin.create_realm(payload=payload)
        return JSONResponse(content={"realm": new_realm})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.patch("/update-realm")
async def updateRealm(request:Request,payload : dict):
    try:
        realm = request._query_params.get("realm-name")
        print(f"realm:{realm}")
        update_realm = keycloak_admin.update_realm(realm_name=realm ,
                                                payload=payload)
        return JSONResponse(content={"update_realm" : update_realm})
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=str(e))
    

@router.delete("/delete-realm")
async def deleteRealm(request : Request):

    try:
        realm = request._query_params.get("realm")
        delete_realm = keycloak_admin.delete_realm(realm_name=realm)
        return JSONResponse(content={"delete_realm" : realm})
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT , detail=str(e))
    

@router.get("/getallUsers")
async def GetAllUsers():
    try:
        all_users = keycloak_admin.get_users()
        return JSONResponse(all_users)
        
    except Exception as e:
        # Tangkap dan tangani kesalahan yang terjadi
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/getuser/{user_id}")
async def GetUserbyId(user_id:str, ):
    try:

        if not user_id :
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="user not found")
        
        user_info = keycloak_admin.get_user(user_id=user_id)
        return JSONResponse(content=user_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

@router.post("/createuser")
async def CreateUser( payload: dict,):
    try:
                new_user_id = keycloak_admin.create_user(payload=payload)
                return JSONResponse(content={'user_id': new_user_id}) 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.patch("/admin-update/{user_id}")
async def UpdateUser(user_id : str ,payload: dict):
    try:
        update_user = keycloak_admin.update_user(user_id=user_id, payload=payload)
        return JSONResponse(content={'updated successfully' : update_user})
    
    except Exception as e:
            print(user_id)
            raise HTTPException(status_code=404, detail=str(e))
        


@router.delete("/userdelete/{user_id}")
async def DeleteUser(user_id: str):
    try:
        deleteUser = keycloak_admin.delete_user(user_id=user_id)
        return JSONResponse(content={'Delete User' : {deleteUser}})
    except Exception as e :
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    


@router.get("/get-client/{client_id}")
async def get_client(client_id: str):
    try:
        getClient = keycloak_admin.get_client(client_id)
        return getClient
    except keycloak.exceptions.KeycloakGetError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/get-client-id/{client_id}")
async def get_client(client_id: str):
    try:
        getClient = keycloak_admin.get_client_id(client_id)
        return JSONResponse(content={'client_id': getClient})
    except keycloak.exceptions.KeycloakGetError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))



@router.patch("/update-client")
async def update_client(request: Request, payload: dict):

        
    client_id = request.query_params.get('clientId')
    
    
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID is required in the payload"
        )
        
    try:
        update_client_response = keycloak_admin.update_client( client_id=client_id, payload=payload)
        return JSONResponse(content={'Updated Client ' : update_client_response})
    

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
    