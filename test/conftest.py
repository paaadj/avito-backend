import pytest
import fakeredis
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app import app
from database.base import get_session, Base
from database.redis import get_redis
from schemas.user import User
from schemas.banner import Banner, Tag, Feature


DB_URL = "sqlite:///:memory:"
ADMIN_TOKEN = ""
USER_TOKEN = ""

engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
Session = sessionmaker(engine, expire_on_commit=False)

app_client = TestClient(app)
r = fakeredis.FakeStrictRedis()


@pytest.fixture(scope="session")
def client():
    yield app_client


@pytest.fixture(scope="session")
def admin_token():
    yield ADMIN_TOKEN


@pytest.fixture(scope="session")
def user_token():
    yield USER_TOKEN


def create_tables():
    global ADMIN_TOKEN, USER_TOKEN
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = Session()
    #  Создание админа
    User.add(session=session, username="admin", password="admin", is_admin=True)
    #  Создание обычного пользователя
    User.add(session=session, username="user", password="user")

    response = app_client.post(
        "/token", data={"username": "admin", "password": "admin"}
    )
    ADMIN_TOKEN = response.json()["access_token"]
    response = app_client.post("/token", data={"username": "user", "password": "user"})
    USER_TOKEN = response.json()["access_token"]

    for _ in range(3):
        tag = Tag.add(session=session)
        feature = Feature.add(session=session)
        session.add(tag)
        session.add(feature)

    tags = Tag.get_tags_by_id(session=session, tag_ids=[1, 3])
    banner = Banner.add(
        session=session,
        tags=tags,
        feature_id=1,
        content={"title": "some_title", "text": "some_text", "url": "some_url"},
    )
    session.add(banner)
    tags = Tag.get_tags_by_id(session=session, tag_ids=[2, 3])
    banner = Banner.add(
        session=session,
        tags=tags,
        feature_id=2,
        content={"title": "some_title1", "text": "some_text1", "url": "some_url1"},
    )
    session.add(banner)
    banner = Banner.add(
        session=session,
        tags=tags,
        feature_id=3,
        content={"title": "some_title1", "text": "some_text1", "url": "some_url1"},
        is_active=False,
    )
    session.add(banner)
    session.commit()


#  Очистка кеша редис
@pytest.fixture(scope="function", autouse=True)
def flush_redis():
    r.flushall()


@pytest.fixture(scope="session", autouse=True)
def setup():
    create_tables()


def fake_session():
    session = Session()
    yield session
    session.close()


#  Пересоздание бд, если проводились изменения в таблицах
@pytest.fixture(scope="function")
def resetup():
    yield
    create_tables()


def fake_redis():
    yield r
    r.close()


app.dependency_overrides[get_session] = fake_session
app.dependency_overrides[get_redis] = fake_redis
