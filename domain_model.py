import dataclasses
from datetime import date


@dataclasses.dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int

class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: date | None) -> None:
        self.reference = ref
        self.sku = sku
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, line: OrderLine) -> None:
        self.available_quantity -= line.qty
