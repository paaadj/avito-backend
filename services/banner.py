import pickle
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload, Session
from schemas.banner import Banner, Tag, Feature
from schemas.pydantic_models import BannerCreate, BannerPatch
from schemas.user import User
from services.user import UserService
from services.celery_tasks import delete_banners_by_tag, delete_banners_by_feature


user_service = UserService()


class BannerService:
    def get_banner_to_user(
            self,
            session: Session,
            redis_client,
            use_last_revision: bool,
            user: User,
            tag_id: int = None,
            feature_id: int = None,
    ):
        try:
            cache_key = f"{tag_id}_{feature_id}"

            if not use_last_revision:
                banner = None
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    banner = pickle.loads(cached_result)
                if banner:
                    if banner.is_active or user.is_admin:
                        return banner
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Пользователь не имеет доступа"
                    )
            if not Tag.exists(session=session, item_id=tag_id) or not Feature.exists(session=session, item_id=feature_id):
                self.__raise400()
            banner = Banner.get(session=session, feature_id=feature_id, tag_id=tag_id)
            if banner is None:
                exc = HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Баннер не найден"
                )
                raise exc
            if not banner.is_active and not user.is_admin:
                exc = HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Пользователь не имеет доступа"
                )
                raise exc
            redis_client.set(cache_key, pickle.dumps(banner), ex=300)
            return banner
        except ValueError:
            self.__raise400()
            return None

    def get_banners(
            self,
            session: Session,
            user: User = Depends(user_service.get_current_user),
            feature_id: int = None,
            tag_id: int = None,
            limit: int = None,
            offset: int = None,
    ):
        user_service.check_admin(user)
        if limit is not None and limit < 1:
            self.__raise400(detail="Значение limit не может быть < 1")
        if offset is not None and offset < 1:
            self.__raise400(detail="Значение offset не может быть < 1")
        banners = Banner.get_by_one_tag_and_feature(
            session=session,
            feature_id=feature_id,
            tag_id=tag_id,
            limit=limit,
            offset=offset,
        )
        banners_response = [banner.to_admin_response() for banner in banners]
        return banners_response

    def create_banner(
            self,
            banner: BannerCreate,
            user: User,
            session: Session,
    ):
        try:
            user_service.check_admin(user)
            banners = Banner.get_by_tags_and_feature(session=session, tag_ids=banner.tag_ids, feature_id=banner.feature_id)
            if len(banners) != 0:
                self.__raise400(detail="Нарушение однозначности")
            tags = self.get_tags_by_id(session=session, tag_ids=banner.tag_ids)
            banner = Banner.add(
                session=session,
                feature_id=banner.feature_id,
                tags=tags,
                content=banner.content,
                is_active=banner.is_active,
            )
            return {'banner_id': banner.id}
        except ValueError:
            self.__raise400()
            return None
        except IntegrityError:
            self.__raise400()
            return None

    def update_banner(
            self,
            session: Session,
            item_id: int,
            user: User,
            new_banner: BannerPatch,
    ):
        user_service.check_admin(user)
        try:
            banner_to_update = session.get(Banner, item_id, options=[selectinload(Banner.tags)])
            if banner_to_update is None:
                self.__raise400()
            tags = []
            if new_banner.tag_ids:
                banners = Banner.get_by_tags_and_feature(
                    session=session,
                    tag_ids=new_banner.tag_ids,
                    feature_id=new_banner.feature_id
                )
                if len(banners) != 0:
                    if banners[0] != banner_to_update:
                        self.__raise400(detail="Нарушение однозначности")
                tags = self.get_tags_by_id(session=session, tag_ids=new_banner.tag_ids)
            banner_to_update.update(
                tags=tags,
                feature_id=new_banner.feature_id,
                content=new_banner.content,
                is_active=new_banner.is_active,
            )
            if session.is_modified(banner_to_update):
                session.commit()
            return "OK"
        except ValueError:
            self.__raise400()
            return None
        except IntegrityError:
            self.__raise400()
            return None

    def delete_banner(
            self,
            session: Session,
            item_id: int,
            user: User,
    ):
        user_service.check_admin(user)
        if Banner.exists(session=session, item_id=item_id):
            Banner.delete(session=session, item_id=item_id)
        else:
            self.__raise400()

    @staticmethod
    def create_tag(session: Session, user: User):
        user_service.check_admin(user)
        tag = Tag.add(session=session)
        return tag

    @staticmethod
    def create_feature(session: Session, user: User):
        user_service.check_admin(user)
        feature = Feature.add(session=session)
        return feature

    @staticmethod
    def __raise400(detail: str = ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Некорректные данные.{detail}",
        )

    def get_tags_by_id(self, session: Session, tag_ids: list[int]):
        tags = Tag.get_tags_by_id(
            tag_ids=tag_ids,
            session=session,
        )
        if None in tags:
            self.__raise400(detail="Один или несколько тегов отсутствуют")
        return tags


    def delete_banners_by_tag_or_feature(
            self,
            feature_id: int = None,
            tag_id: int = None,
    ):
        if feature_id and tag_id:
            self.__raise400()
        task = None
        if feature_id:
            task = delete_banners_by_feature.delay(feature_id)
        if tag_id:
            task = delete_banners_by_tag.delay(tag_id)
