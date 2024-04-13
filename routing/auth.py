from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database.base import get_session
from services.config import settings
from services.user import UserService
from schemas.user import User
from schemas.pydantic_models import UserCreate, UserResponse


router = APIRouter()
JWT_SECRET = settings.SECRET_KEY
user_service = UserService()


@router.post("/token", tags=["auth"])
async def get_token(
        session: Session = Depends(get_session),
        form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Получить токен по данным пользователя
    :param form_data: Форма с данными пользователя (username, password)
    :return: Если данные не верны -- 400, иначе ответ с access_token}
    """
    user = user_service.authenticate_user(
        session=session,
        username=form_data.username,
        password=form_data.password
    )
    return user_service.get_access_token(user=user)


@router.post("/register", tags=["auth"], response_model=UserResponse)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """
    Регистрация обычного пользователя
    :param user: Данные пользователя (username, password)
    :return: Если пользователь уже существует или некорректные данные, то 400,
     иначе ответ с ID и username нового пользователя
    """
    user = user_service.create_user(session=session, user=user)
    return user.to_response()


@router.post("/register_admin", tags=["auth"], response_model=UserResponse)
def register_admin(user: UserCreate, session: Session = Depends(get_session)):
    """
    Регистрация администратора
    :param user: Данные пользователя (username, password)
    :return: Если пользователь уже существует или некорректные данные,
     то 400, иначе ответ с ID и username нового пользователя
    """
    user = user_service.create_user(session=session, user=user, is_admin=True)
    return user.to_response()


@router.get("/users/me", response_model=UserResponse, tags=["auth"])
def get_user(
        user: User = Depends(user_service.get_current_user),
):
    """
    Получение данных о текущем пользователе
    :return: Пользоавтель, если данные корректны, если данные неверны,
     то 401, если данные в неправильном формате
    (password < 8 символов), то 400
    """
    return user.to_response()
