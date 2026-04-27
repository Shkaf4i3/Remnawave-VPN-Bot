from ..dto import UserDto
from ..model import User


def map_user(user: User) -> UserDto:
    return UserDto(
        id=user.id,
        tg_id=user.tg_id,
        balance=user.balance,
        role=user.role,
        created_at=user.created_at,
        is_blocked=user.is_blocked,
        updated_at=user.updated_at,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.last_name,
        referred_by_id=user.referred_by_id,
    )
