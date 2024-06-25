import dataclasses
from datetime import date

from types import Quantity, Reference, Sku


@dataclasses.dataclass(frozen=True)
class OrderLine:
    order_id: Reference
    sku: Sku
    qty: Quantity


class Batch:
    _allocations: set[OrderLine]

    def __init__(self, ref: Reference, sku: Sku, qty: Quantity, eta: date | None) -> None:
        self.reference = ref
        self.sku = sku
        self._purchased_quantity = qty
        self.eta = eta
        self._allocations = set()

    def allocate(self, line: OrderLine):
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
