import abc
from typing import Generic, TypeVar

import src.domain as domain

M = TypeVar('M')


class AbstractRepository(Generic[M], abc.ABC):
    @abc.abstractmethod
    def add(self, batch: M):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, reference) -> M:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository[domain.Batch]):
    def __init__(self, session):
        self.session = session

    def add(self, batch):
        self.session.add(batch)

    def get(self, reference):
        return self.session.query(domain.Batch).filter_by(reference=reference).one()

    def list(self):
        return self.session.query(domain.Batch).all()


class FakeRepository(AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)

    def add(self, batch):
        self._batches.add(batch)

    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)

    def list(self):
        return list(self._batches)
