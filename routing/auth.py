from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.base import get_session
from services.config import settings
from services.user import UserService
from schemas.user import UserCreate, UserResponse, User


router = APIRouter()
JWT_SECRET = settings.SECRET_KEY
user_service = UserService()


@router.post("/token", tags=["auth"])
async def get_token(
        session: Session = Depends(get_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = user_service.authenticate_user(session, form_data.username, form_data.password)
    return user_service.get_access_token(user=user)


@router.post("/register", tags=["auth"], response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session)):
    user = user_service.create_user(session=session, user=user)
    return user.to_response()


@router.post("/register_admin", tags=["auth"], response_model=UserResponse)
def register_admin(user: UserCreate, session: Session = Depends(get_session)):
    user = user_service.create_user(session=session, user=user, is_admin=True)
    return user.to_response()


@router.get("/users/me", response_model=UserResponse, tags=["auth"])
def get_user(
        user: User = Depends(user_service.get_current_user),
):
    return user.to_response()

