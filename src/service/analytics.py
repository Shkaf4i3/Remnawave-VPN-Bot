from datetime import datetime, timedelta, timezone

from ..repo import UnitOfWork, UserRepo, PaymentRepo
from ..dto import (
    QueryUsersDto,
    AnalyticsUsersDto,
    QueryPaymentStatsDto,
)
from .cache import CacheService


class AnalyticsService:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        user_repo: UserRepo,
        payment_repo: PaymentRepo,
        cache_service: CacheService,
    ) -> None:
        self.unit_of_work = unit_of_work
        self.user_repo = user_repo
        self.payment_repo = payment_repo
        self.cache_service = cache_service


    async def get_analytics_users(
        self,
    ) -> AnalyticsUsersDto:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        yesterday_start = today_start - timedelta(days=1)
        week_start = today_start - timedelta(days=today_start.weekday())
        month_start = today_start.replace(day=1)
        users_yesterday = await self.user_repo.get_count_users_between(
            start_date=yesterday_start,
            end_date=today_start,
        )
        users_today = await self.user_repo.get_count_users_since(start_date=today_start)
        users_week = await self.user_repo.get_count_users_since(start_date=week_start)
        users_month = await self.user_repo.get_count_users_since(start_date=month_start)
        users_total = await self.user_repo.get_count_users_total()
        payments_yesterday = await self.payment_repo.stats_between(
            start_date=yesterday_start,
            end_date=today_start,
        )
        payments_today = await self.payment_repo.stats_since(start_date=today_start)
        payments_week = await self.payment_repo.stats_since(start_date=week_start)
        payments_month = await self.payment_repo.stats_since(start_date=month_start)
        payments_total = await self.payment_repo.total_stats()
        users = QueryUsersDto(
            yesterday=users_yesterday,
            today=users_today,
            week=users_week,
            month=users_month,
            total=users_total,
        )
        payments = QueryPaymentStatsDto(
            yesterday=payments_yesterday,
            today=payments_today,
            week=payments_week,
            month=payments_month,
            total=payments_total,
        )
        return AnalyticsUsersDto(users=users, payments=payments)
