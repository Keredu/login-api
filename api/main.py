import os
import secrets
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from login_db.enums import TokenStatus, TokenType, UserStatus
from login_db.connection import Session
from login_db.functions.token import create_jwt_token, insert_token
from login_db.functions.user import (
    insert_user,
    is_username_password_valid,
    modify_user_password,
    retrieve_user,
)
from login_db.models import Token, User
from login_db.exceptions import DatabaseInsertionError, MissingEnvironmentVariableError
#from api.logger import get_logger
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr
from sqlalchemy.exc import IntegrityError

########################## Logging ##########################
# Initialize logger
#logger = get_logger(__name__)
#logger.info("Starting FastAPI server...")

################# Constants & Environment Variables ###############
# TODO: all the environment variables as strings??????
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET_KEY = os.getenv("SECRET_KEY")
if not all([ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY]):
    #logger.critical("Missing environment variables.")
    raise MissingEnvironmentVariableError("Missing environment variables.")

########################## FastAPI ##########################
# Define a lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # On startup
    pass
    yield
    # On shutdown
    pass

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# Define a list of origins that should be allowed to make requests
origins = [
    "http://localhost:3000",  # React's default port
    "http://localhost:8000",  # FastAPI's default port
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


########################### Authentication ###########################

class UserLogin(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: UserLogin):
    with Session() as session:
        #logger.debug(f"Calling login with data: {data}")
        if is_username_password_valid(data.username, data.password, session=session):
            user = retrieve_user(username_or_email=data.username, session=session)
            if user.status == UserStatus.PENDING:
                #logger.info(f"Attempt to login with pending user: {data.username}")
                raise HTTPException(status_code=400, detail="Pending user.")
            
            elif user.status == UserStatus.BANNED:
                #logger.info(f"Attempt to login with banned user: {data.username}")
                raise HTTPException(status_code=400, detail="Banned user.")
            
            elif user.status == UserStatus.DELETED:
                #logger.info(f"Attempt to login with deleted user: {data.username}")
                raise HTTPException(status_code=400, detail="Deleted user.")
            
            elif user.status == UserStatus.INACTIVE:
                #logger.info(f"Attempt to login with inactive user: {data.username}")
                raise HTTPException(status_code=400, detail="Inactive user.")
            
            expiration_time = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            data={"sub": user.id, "exp": expiration_time}
            token = create_jwt_token(data=data, session=session)
            return JSONResponse(content={"token": token}, status_code=200)
        else:
            #logger.info(f"Invalid login attempt for username: {data.username}")
            raise HTTPException(status_code=400, detail="Incorrect username and password combination")


class UserRegistration(BaseModel):
    username: str
    email: EmailStr
    password: str

@app.post("/register/")
async def register(data: UserRegistration):
    #logger.debug(f"Calling register with data: {data}")
    try:
        userdata = data.__dict__
        userdata['status'] = UserStatus.ACTIVE # TODO: change this to PENDING
        with Session() as session:
            insert_user(userdata=userdata, session=session)
        return JSONResponse(content={"message": "User registered successfully."}, status_code=200)
    
    except IntegrityError as e:
        #logger.info(f"IntegrityError: {str(e)}")
        raise HTTPException(status_code=400, detail="Username or email already exists.")
    
    except DatabaseInsertionError as e:
        #logger.info(f"DatabaseInsertionError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        #logger.critical(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

class ValidateToken(BaseModel):
    token: str
    # type: str or TokenType (TokenType is an enum represented by int) NOTE: Problems?
@app.post("/validate-token/")
async def validate_token(data: ValidateToken):
    #logger.debug(f"Calling validate-token with data: {data}")
    with Session() as session:
        token = session.query(Token).filter(
            Token.token == data.token,
            Token.expiration_time > datetime.utcnow()
        ).first()

        if token is not None and token.status == TokenStatus.ACTIVE:
            return JSONResponse(content={"message": "Token is valid."}, status_code=200)
    
    raise HTTPException(status_code=400, detail="Invalid or expired token")

########################### Logout ###########################
class LogoutToken(BaseModel):
    token: str

@app.post("/logout/")
async def logout(data: ValidateToken):
    with Session() as session:
        # Retrieve the token from the database
        # TODO: is it possible to improve this query?
        # token = session.query(Token).filter(Token.token == data.token,
        #                                     Token.type == TokenType.ACCESS).first()
        token = session.query(Token).filter(Token.token == data.token,
                                            Token.status == TokenStatus.ACTIVE).first()
        if token:
            # Invalidate the token
            token.status = TokenStatus.LOGGED_OUT
            session.commit()
            return JSONResponse(content={"message": "Logged out successfully."}, status_code=200)
    
    raise HTTPException(status_code=400, detail="Invalid token.")


########################### Password Reset ###########################    
def send_reset_email(email: str, token: str):
    #logger.critical(f"Sending http://localhost:3000/reset-password?token={token} to {email}")
    pass

class ForgottenPasswordRequest(BaseModel):
    email: str

@app.post("/forgotten-password/")
async def forgot_password(data: ForgottenPasswordRequest):
    #logger.debug(f"Calling forgot_password with data: {data}")
    try:
        with Session() as session:
            user = session.query(User).filter(User.email == data.email).first()
            if user is not None:
                token = secrets.token_urlsafe(32)
                expiration_time = datetime.utcnow() + timedelta(minutes=10)
                insert_token(user_id=user.id,
                             token=token,
                             type=TokenType.RESET_PASSWORD,
                             status=TokenStatus.ACTIVE,
                             expiration_time=expiration_time,
                             session=session)
                send_reset_email(user.email, token)
            else:
                # TODO: log this to a specific file/db -> IP, email, time, ...
                pass
        return JSONResponse(content={"message": "If your email is registered, you will receive a password reset link."},
                            status_code=200)
    except Exception as e:
        #logger.critical(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


class ResetPasswordRequest(BaseModel):
    token: str
    password: str

@app.post("/reset-password/")
async def reset_password(data: ResetPasswordRequest):
    #logger.debug(f"Calling reset-password with data: {data}")
    with Session() as session:
        reset_token = session.query(Token).filter(
            Token.token == data.token,
            Token.expiration_time > datetime.utcnow(),
            Token.type == TokenType.RESET_PASSWORD,
        ).first()

    if reset_token is not None and reset_token.status == TokenStatus.ACTIVE:
        modify_user_password(reset_token.user_id, data.password, session=session)
        reset_token.status = TokenStatus.USED
        session.commit()
        # TODO: log this to a specific file/db -> IP, email, time, ... + add field last time password was reset?
        return JSONResponse(content={"message": "Password reset successfully."}, status_code=200)

    raise HTTPException(status_code=400, detail="Invalid or expired token")


########################### Protected Routes ###########################

# NOTE: TO BE USED
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(token: str = Depends(oauth2_scheme)): # TODO: Understand how this works (Depends)
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception
    
# NOTE: datetime.utcfromtimestamp(jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])['exp'])
# We have to use utc always.