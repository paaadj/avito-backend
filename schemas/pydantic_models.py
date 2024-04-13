from pydantic import BaseModel


class BannerResponse(BaseModel):
    content: dict


class BannerCreate(BaseModel):
    tag_ids: list[int]
    feature_id: int
    content: dict
    is_active: bool


class BannerPatch(BaseModel):
    tag_ids: list[int] = None
    feature_id: int = None
    content: dict = None
    is_active: bool = None


class BannerAdminResponse(BaseModel):
    banner_id: int
    tag_ids: list[int]
    feature_id: int
    content: dict
    is_active: bool
    created_at: str
    updated_at: str = None


class UserCreate(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
