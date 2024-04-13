from datetime import datetime
from passlib.hash import bcrypt
from sqlalchemy import Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import validates
from sqlalchemy.orm import Session
from database.base import Base
from schemas.pydantic_models import UserResponse


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    created_at = Column(DateTime, default=datetime.now())
    is_admin = Column(Boolean, default=False)

    @validates("username")
    def validate_username(self, _, username):
        if len(username) < 4:
            raise ValueError("Имя пользователя должно состоять из хотя бы 4 символов")
        return username

    def verify_password(self, password):
        return bcrypt.verify(password, self.password)

    @classmethod
    def add(cls, session: Session, username, password, is_admin=False):
        user = cls(username=username, password=bcrypt.hash(password), is_admin=is_admin)
        session.add(user)
        session.commit()
        return user

    def to_response(self):
        return UserResponse(
            id=self.id,
            username=self.username,
        )
