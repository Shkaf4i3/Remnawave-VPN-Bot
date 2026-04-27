from ..dto import PaymentDto
from ..model import Payment


def map_payment(payment: Payment) -> PaymentDto:
    return PaymentDto(
        id=payment.id,
        tg_id=payment.tg_id,
        invoice_id=payment.invoice_id,
        amount=payment.amount,
        status=payment.status,
        created_at=payment.created_at,
    )
