import pytest

from datetime import date, timedelta

from src.exceptions import OutOfStock
from src.domain import Batch, OrderLine, allocate
from src.types import Reference, Sku, Quantity


today = date.today()
tomorrow = date.today() + timedelta(days=1)
later = date.today() + timedelta(days=10)


def make_batch_and_line(sku, batch_qty, line_qty):
    return (
        Batch(Reference("batch-001"), sku, batch_qty, eta=date.today()),
        OrderLine(Reference("order-123"), sku, line_qty)
    )


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch(Reference("batch-001"), Sku("SMALL-TABLE"), qty=Quantity(20), eta=date.today())
    line = OrderLine(Reference('order-ref'), Sku("SMALL-TABLE"), Quantity(2))
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required():
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch(Reference("batch-001"), Sku("UNCOMFORTABLE-CHAIR"), Quantity(100), eta=None)
    different_sku_line = OrderLine(Reference("order-123"), Sku("EXPENSIVE-TOASTER"), Quantity(10))
    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines():
    batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
    batch.deallocate(unallocated_line)
    assert batch.available_quantity == 20


def test_allocation_is_idempotent():
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)
    assert batch.available_quantity == 18


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(Reference("in-stock-batch-ref"), Sku("HIGHBROW-POSTER"), Quantity(100), eta=None)
    shipment_batch = Batch(
        Reference("shipment-batch-ref"),
        Sku("HIGHBROW-POSTER"),
        Quantity(100),
        eta=tomorrow,
    )
    line = OrderLine(Reference("oref"), Sku("HIGHBROW-POSTER"), Quantity(10))
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.reference


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(Reference("in-stock-batch"), Sku("RETRO-CLOCK"), Quantity(100), eta=None)
    shipment_batch = Batch(Reference("shipment-batch"), Sku("RETRO-CLOCK"), Quantity(100), eta=tomorrow)
    line = OrderLine(Reference("oref"), Sku("RETRO-CLOCK"), Quantity(10))
    allocate(line, [in_stock_batch, shipment_batch])
    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(Reference("speedy-batch"), Sku("MINIMALIST-SPOON"), Quantity(100), eta=today)
    medium = Batch(Reference("normal-batch"), Sku("MINIMALIST-SPOON"), Quantity(100), eta=tomorrow)
    latest = Batch(Reference("slow-batch"), Sku("MINIMALIST-SPOON"), Quantity(100), eta=later)
    line = OrderLine(Reference("order1"), Sku("MINIMALIST-SPOON"), Quantity(10))
    allocate(line, [medium, earliest, latest])
    assert earliest.available_quantity == 90


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(Reference('batch1'), Sku('SMALL-FORK'), Quantity(10), eta=today)
    allocate(OrderLine(Reference('order1'), Sku('SMALL-FORK'), Quantity(10)), [batch])
    with pytest.raises(OutOfStock, match='SMALL-FORK'):
        allocate(OrderLine(Reference('order2'), Sku('SMALL-FORK'), Quantity(1)), [batch])
