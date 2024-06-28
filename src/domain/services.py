from src.exceptions import OutOfStock
from src.custom_types import Reference

from .models import OrderLine, Batch


def allocate(line: OrderLine, batches: list[Batch]) -> Reference:
    try:
        batch = next(
            b for b in sorted(batches) if b.can_allocate(line)
        )
        batch.allocate(line)
        return batch.reference
    except StopIteration:
        raise OutOfStock(f'Out of stock for sku {line.sku}')
