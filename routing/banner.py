from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database.redis import get_redis
from database.base import get_session
from services.banner import BannerService
from services.user import UserService
from services.celery_tasks import delete_banners_by_feature, delete_banners_by_tag, celery
from schemas.user import User
from schemas.banner import Tag, Feature
from schemas.pydantic_models import BannerResponse, BannerCreate, BannerPatch

router = APIRouter()
banner_service = BannerService()
user_service = UserService()


@router.get("/user_banner", response_model=BannerResponse)
async def get_user_banner(
        tag_id: int,
        feature_id: int,
        use_last_revision: bool = False,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
        redis_client=Depends(get_redis)
):
    return banner_service.get_banner_to_user(
        session=session,
        tag_id=tag_id,
        feature_id=feature_id,
        use_last_revision=use_last_revision,
        user=user,
        redis_client=redis_client,
    )


@router.get("/banner")
async def get_banners(
        user: User = Depends(user_service.get_current_user),
        feature_id: int = None,
        tag_id: int = None,
        limit: int = None,
        offset: int = None,
        session: Session = Depends(get_session),
):
    return banner_service.get_banners(
        session=session,
        user=user,
        feature_id=feature_id,
        tag_id=tag_id,
        limit=limit,
        offset=offset,
    )


@router.post("/banner", status_code=201)
async def create_banner(
        banner: BannerCreate,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    return banner_service.create_banner(
        banner=banner,
        user=user,
        session=session,
    )


@router.delete("/banner/delete", status_code=204)
async def delete_banners_by_tag_or_feature(
        feature_id: int = None,
        tag_id: int = None,
        user: User = Depends(user_service.get_current_user),
):
    user_service.check_admin(user)
    banner_service.delete_banners_by_tag_or_feature(feature_id, tag_id)


@router.patch("/banner/{item_id}")
async def update_banner(
        item_id: int,
        banner: BannerPatch,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session)
):
    return banner_service.update_banner(
        session=session,
        item_id=item_id,
        user=user,
        new_banner=banner,
    )


@router.delete("/banner/{item_id}", status_code=204)
async def delete_banner(
        item_id: int,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    return banner_service.delete_banner(
        session=session,
        item_id=item_id,
        user=user,
    )


@router.post("/tag")
async def create_tag(
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    return banner_service.create_tag(session=session, user=user)


@router.delete("/tag/{item_id}", status_code=204)
async def delete_tag(
        item_id: int,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    user_service.check_admin(user)
    Tag.delete(session=session, item_id=item_id)
    return


@router.post("/feature")
async def create_feature(
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    return banner_service.create_feature(session=session, user=user)


@router.delete("/feature/{item_id}", status_code=204)
async def delete_feature(
        item_id: int,
        user: User = Depends(user_service.get_current_user),
        session: Session = Depends(get_session),
):
    user_service.check_admin(user)
    Feature.delete(session=session, item_id=item_id)
    return


@router.get('/tags')
async def get_tags(session: Session = Depends(get_session)):
    return {"tags": Tag.all(session=session)}


@router.get("/features")
async def get_features(session: Session = Depends(get_session)):
    return {"features": Feature.all(session=session)}
