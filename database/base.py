from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from services.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)
Base = declarative_base()
Session = sessionmaker(engine, expire_on_commit=False)


def init_models():
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)


def get_session() -> Session:
    session = Session()
    try:
        yield session
    finally:
        session.close()
