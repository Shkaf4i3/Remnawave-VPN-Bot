from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..model import Payment
from ..dto import QueryPaymentSinglePeriodStatsDto


class PaymentRepo:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


    async def save_payment(self, payment: Payment) -> Payment:
        self.session.add(instance=payment)
        await self.session.flush()
        await self.session.refresh(instance=payment)
        return payment


    async def get_payment_by_invoice_id(self, invoice_id: str) -> Payment | None:
        stmt = select(Payment).where(Payment.invoice_id == invoice_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def get_payment_by_tg_id(self, tg_id: int) -> Payment | None:
        stmt = select(Payment).where(Payment.tg_id == tg_id)
        result = await self.session.execute(statement=stmt)
        return result.scalar()


    async def stats_since(self, start_date: datetime) -> QueryPaymentSinglePeriodStatsDto:
        stmt = (
            select(
                func.count().label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("total_amount"),
            )
            .where(Payment.created_at >= start_date)
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return QueryPaymentSinglePeriodStatsDto(
            count=row.count,
            total_amount=row.total_amount
        )

    async def stats_between(
        self,
        start_date: datetime,
        end_date: datetime,
    ) -> QueryPaymentSinglePeriodStatsDto:
        stmt = (
            select(
                func.count().label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("total_amount"),
            )
            .where(
                Payment.created_at >= start_date,
                Payment.created_at < end_date
            )
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return QueryPaymentSinglePeriodStatsDto(
            count=row.count,
            total_amount=row.total_amount
        )


    async def total_stats(self) -> QueryPaymentSinglePeriodStatsDto:
        stmt = (
            select(
                func.count().label("count"),
                func.coalesce(func.sum(Payment.amount), 0).label("total_amount"),
            )
            .select_from(Payment)
        )
        result = await self.session.execute(stmt)
        row = result.one()
        return QueryPaymentSinglePeriodStatsDto(
            count=row.count,
            total_amount=row.total_amount
        )
