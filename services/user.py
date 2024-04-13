import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from services.config import settings
from database.base import get_session
from schemas.user import User
from schemas.pydantic_models import UserCreate


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class UserService:
    def create_user(self, session: Session, user: UserCreate, is_admin: bool = False) -> User:
        try:
            existing_user = session.query(User).filter(User.username == user.username).scalar()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Пользователь с этим именем пользователя уже существует"
                )
            if len(user.password) < 8:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Длина пароля '{user.password}' {len(user.password)} < 8"
                )
            new_user = User.add(session=session, username=user.username, password=user.password, is_admin=is_admin)
            return new_user
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{exc}"
            ) from exc

    def authenticate_user(self, session: Session, username: str, password: str) -> User:
        try:
            user = session.query(User).filter(User.username == username).scalar()
            if user is None or not user.verify_password(password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Неверное имя пользователя или пароль",
                )
            return user
        except ValueError as validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный формат, {validation_error}"
            ) from validation_error

    def get_access_token(self, user: User):
        user_obj = {
            "username": user.username,
            "is_admin": user.is_admin,
        }
        access_token = jwt.encode(user_obj, key=settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }

    def get_current_user(self, session: Session = Depends(get_session), access_token: str = Depends(oauth2_scheme)):
        try:
            if access_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated"
                )
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user = session.query(User).filter(User.username == payload.get('username')).scalar()
            if user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Пользователь не найден"
                )
            return user
        except ValueError as validation_error:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неверный формат: {validation_error}"
            ) from validation_error
        except jwt.exceptions.DecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            ) from exc

    def check_admin(self, user: User):
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не имеет доступа"
            )
