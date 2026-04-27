from ..dto import PaymentDto
from ..model import Payment, PaymentStatus
from ..mappings import payment_mappings
from ..repo import PaymentRepo, UnitOfWork, transactional


class PaymentService:
    def __init__(self, payment_repo: PaymentRepo, unit_of_work: UnitOfWork) -> None:
        self.payment_repo = payment_repo
        self.unit_of_work = unit_of_work


    @transactional
    async def save_payment(self, tg_id: int, invoice_id: str, amount: float) -> PaymentDto:
        new_payment = Payment(
            tg_id=tg_id,
            invoice_id=invoice_id,
            amount=amount,
        )
        saved_payment = await self.payment_repo.save_payment(payment=new_payment)
        return payment_mappings.map_payment(payment=saved_payment)


    async def get_payment_by_tg_id(self, tg_id: int) -> PaymentDto | None:
        existing_payment = await self.payment_repo.get_payment_by_tg_id(tg_id=tg_id)
        if not existing_payment:
            raise KeyError(f"Payment with tg_id {tg_id} not found")
        return payment_mappings.map_payment(payment=existing_payment)


    async def get_payment_by_invoice_id(self, invoice_id: str) -> PaymentDto | None:
        existing_payment = await self.payment_repo.get_payment_by_invoice_id(invoice_id=invoice_id)
        if not existing_payment:
            raise KeyError(f"Payment with invoice_id {invoice_id} not found")
        return payment_mappings.map_payment(payment=existing_payment)


    @transactional
    async def update_payment_by_invoice_id(self, invoice_id: str, status: PaymentStatus) -> None:
        existing_payment = await self.payment_repo.get_payment_by_invoice_id(
            invoice_id=invoice_id,
        )
        if not existing_payment:
            raise KeyError(f"Payment with invoice_id {invoice_id} not found")
        existing_payment.status = status
        await self.payment_repo.save_payment(payment=existing_payment)
