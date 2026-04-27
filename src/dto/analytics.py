from pydantic import BaseModel


class QueryUsersDto(BaseModel):
    yesterday: int
    today: int
    week: int
    month: int
    total: int


class QueryPaymentSinglePeriodStatsDto(BaseModel):
    count: int
    total_amount: float

class QueryPaymentStatsDto(BaseModel):
    yesterday: QueryPaymentSinglePeriodStatsDto
    today: QueryPaymentSinglePeriodStatsDto
    week: QueryPaymentSinglePeriodStatsDto
    month: QueryPaymentSinglePeriodStatsDto
    total: QueryPaymentSinglePeriodStatsDto


class AnalyticsUsersDto(BaseModel):
    users: QueryUsersDto
    payments: QueryPaymentStatsDto
