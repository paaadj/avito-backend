from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    Table,
    exists,
)
from sqlalchemy.orm import relationship, selectinload, Session
from database.base import Base
from schemas.pydantic_models import BannerAdminResponse


banner_tag = Table('banner_tag', Base.metadata,
                   Column(
                       'banner_id',
                       Integer,
                       ForeignKey('banners.id', ondelete="CASCADE")
                   ),
                   Column(
                       'tag_id',
                       Integer,
                       ForeignKey('tags.id', ondelete="CASCADE")
                   ))


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    banners = relationship("Banner", secondary='banner_tag', back_populates="tags")

    @classmethod
    def get_tags_by_id(
            cls,
            tag_ids: list[int],
            session: Session,
    ):
        return [(session.get(cls, tag_id)) for tag_id in tag_ids]

    @classmethod
    def add(cls, session: Session):
        tag = cls()
        session.add(tag)
        session.commit()
        return tag

    @classmethod
    def all(cls, session: Session):
        tags = session.query(cls).all()
        return tags

    @classmethod
    def exists(cls, session: Session, item_id):
        return session.query(exists(cls).where(cls.id == item_id)).scalar()

    @classmethod
    def delete(cls, session: Session, item_id):
        session.query(cls).filter_by(id=item_id).delete()
        session.commit()


class Feature(Base):
    __tablename__ = "features"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    banners = relationship("Banner", back_populates="feature")

    @classmethod
    def add(cls, session: Session):
        feature = cls()
        session.add(feature)
        session.commit()
        return feature

    @classmethod
    def exists(cls, session: Session, item_id):
        return session.query(exists(cls).where(cls.id == item_id)).scalar()

    @classmethod
    def all(cls, session: Session):
        features = session.query(cls).all()
        return features

    @classmethod
    def delete(cls, session: Session, item_id):
        session.query(cls).filter_by(id=item_id).delete()
        session.commit()


class Banner(Base):
    __tablename__ = "banners"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    content = Column(JSON)
    feature_id = Column(Integer, ForeignKey('features.id', ondelete='CASCADE'))
    feature = relationship("Feature", back_populates="banners")
    tags = relationship("Tag", secondary="banner_tag", back_populates="banners")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, onupdate=datetime.now())

    def to_admin_response(self):
        return BannerAdminResponse(
            banner_id=self.id,
            tag_ids=[tag.id for tag in self.tags],
            feature_id=self.feature_id,
            content=self.content,
            created_at=str(self.created_at),
            updated_at=str(self.updated_at),
            is_active=self.is_active
        )

    @classmethod
    def add(cls, session: Session, tags, feature_id, content, is_active=True):
        banner = cls(content=content, tags=tags, feature_id=feature_id, is_active=is_active)
        session.add(banner)
        session.commit()
        return banner

    def update(
            self,
            tags,
            feature_id,
            content,
            is_active
    ):
        if tags:
            self.tags = tags
        if feature_id:
            self.feature_id = feature_id
        if content:
            self.content = content
        if is_active is not None:
            self.is_active = is_active

    @classmethod
    def delete(cls, session: Session, item_id):
        session.query(cls).filter_by(id=item_id).delete()
        session.commit()

    @classmethod
    def exists(cls, session: Session, item_id):
        return session.query(exists(cls).where(cls.id == item_id)).scalar()

    #  Получение баннеров по айди тегов и айди фичи
    @staticmethod
    def get_by_tags_and_feature(session: Session, tag_ids, feature_id):
        banners = session.query(Banner).filter(
            Banner.feature_id == feature_id,
            Banner.tags.any(Tag.id.in_(tag_ids))
        ).all()
        return banners

    @classmethod
    def get_by_one_tag_and_feature(
            cls,
            session: Session,
            feature_id: int = None,
            tag_id: int = None,
            limit: int = None,
            offset: int = None,
    ):
        query = session.query(Banner)
        if feature_id:
            query = query.filter_by(feature_id=feature_id)
        if tag_id:
            query = query.filter(Banner.tags.any(id=tag_id))
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        query = query.options(selectinload(Banner.tags))
        banners = query.all()
        return banners

    @classmethod
    def get(cls, session: Session, feature_id: int, tag_id: int):
        banner = session.query(cls).filter(
            cls.feature_id == feature_id,
            cls.tags.any(id=tag_id)
        ).scalar()
        return banner
