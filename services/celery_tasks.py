from celery import Celery
from services.config import settings
from database.base import get_session
from schemas.banner import Banner

REDIS_URL = (f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/"
             f"{settings.REDIS_CELERY_DB}")

celery = Celery('tasks', broker=REDIS_URL, backend=REDIS_URL)


@celery.task
def delete_banners_by_feature(feature_id):
    session = next(get_session())
    banners = (
        session.query(Banner)
        .filter(Banner.feature_id == feature_id)
        .all()
    )
    for banner in banners:
        session.delete(banner)
    session.commit()
    return


@celery.task
def delete_banners_by_tag(tag_id):
    session = next(get_session())
    banners = (
        session.query(Banner)
        .filter(Banner.tags.any(id=tag_id))
        .all()
    )
    for banner in banners:
        session.delete(banner)
    session.commit()
