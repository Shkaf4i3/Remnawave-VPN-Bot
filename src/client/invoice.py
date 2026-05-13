class Invoice:
    def __init__(self, invoice_id: str, url: str, payment_id: str | None = None) -> None:
        self.invoice_id = invoice_id
        self.url = url
        self.payment_id = payment_id
