"""A small in-memory stand-in for Firestore, used only by the tests.

It mimics the parts of the API EcoBin uses, including transaction semantics:
writes are buffered until commit, discarded on error, and reads after writes
inside a transaction raise (as real Firestore does).
"""

from __future__ import annotations

import itertools
import types
from datetime import datetime, timezone

SERVER_TIMESTAMP = object()
_ids = itertools.count(1)


class Increment:
    def __init__(self, value):
        self.value = value


class FieldFilter:
    def __init__(self, field_path, op_string, value):
        self.field, self.op, self.value = field_path, op_string, value

    def matches(self, data):
        v = data.get(self.field)
        if v is None:
            return False
        return {">": v > self.value, ">=": v >= self.value, "==": v == self.value,
                "<": v < self.value, "<=": v <= self.value}[self.op]


class Conflict(Exception):
    pass


def transactional(func):
    def wrapper(txn, *args, **kwargs):
        try:
            result = func(txn, *args, **kwargs)
        except Exception:
            txn.rollback()
            raise
        txn.commit()
        return result
    return wrapper


fs = types.SimpleNamespace(
    SERVER_TIMESTAMP=SERVER_TIMESTAMP,
    Increment=Increment,
    FieldFilter=FieldFilter,
    transactional=transactional,
    Query=types.SimpleNamespace(DESCENDING="DESCENDING", ASCENDING="ASCENDING"),
)


class Snapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data
        self.exists = data is not None

    def to_dict(self):
        return dict(self._data) if self._data is not None else None


class AggResult:
    def __init__(self, value):
        self.value = value


class Query:
    def __init__(self, client, path, filters=(), order=None, limit_n=None):
        self.client, self.path = client, path
        self.filters, self.order, self.limit_n = list(filters), order, limit_n

    def where(self, *, filter):
        return Query(self.client, self.path, self.filters + [filter], self.order, self.limit_n)

    def order_by(self, field, direction="ASCENDING"):
        return Query(self.client, self.path, self.filters, (field, direction), self.limit_n)

    def limit(self, n):
        return Query(self.client, self.path, self.filters, self.order, n)

    def _docs(self):
        prefix = self.path + "/"
        docs = []
        for key, data in self.client.store.items():
            rest = key[len(prefix):] if key.startswith(prefix) else None
            if rest and "/" not in rest and all(f.matches(data) for f in self.filters):
                docs.append(Snapshot(rest, data))
        if self.order:
            field, direction = self.order
            docs = [d for d in docs if field in d._data]
            docs.sort(key=lambda d: d._data[field], reverse=direction == "DESCENDING")
        if self.limit_n is not None:
            docs = docs[: self.limit_n]
        return docs

    def stream(self):
        return iter(self._docs())

    def count(self, alias=None):
        q = self
        return types.SimpleNamespace(get=lambda: [[AggResult(len(q._docs()))]])


class Collection(Query):
    def document(self, doc_id=None):
        return DocRef(self.client, f"{self.path}/{doc_id or 'auto' + str(next(_ids))}")


class DocRef:
    def __init__(self, client, path):
        self.client, self.path = client, path
        self.id = path.rsplit("/", 1)[1]

    def collection(self, name):
        return Collection(self.client, f"{self.path}/{name}")

    def get(self, transaction=None):
        if transaction is not None and transaction.writes:
            raise RuntimeError("Firestore transactions require all reads before writes")
        return Snapshot(self.id, self.client.store.get(self.path))

    def set(self, data, merge=False):
        self.client.apply("set", self.path, data, merge)


class Transaction:
    def __init__(self, client):
        self.client, self.writes = client, []

    def create(self, ref, data):
        self.writes.append(("create", ref.path, data, False))

    def set(self, ref, data, merge=False):
        self.writes.append(("set", ref.path, data, merge))

    def update(self, ref, data):
        self.writes.append(("update", ref.path, data, True))

    def commit(self):
        for w in self.writes:  # validate first so a failed commit writes nothing
            if w[0] == "create" and w[1] in self.client.store:
                raise Conflict(w[1])
            if w[0] == "update" and w[1] not in self.client.store:
                raise Conflict(w[1])
        for w in self.writes:
            self.client.apply(*w)
        self.writes = []
        self.client.commits += 1

    def rollback(self):
        self.writes = []


class FakeClient:
    def __init__(self):
        self.store: dict[str, dict] = {}
        self.commits = 0

    def collection(self, name):
        return Collection(self, name)

    def transaction(self):
        return Transaction(self)

    def apply(self, op, path, data, merge):
        current = dict(self.store.get(path, {})) if (merge or op == "update") else {}
        for k, v in data.items():
            if isinstance(v, Increment):
                current[k] = current.get(k, 0) + v.value
            elif v is SERVER_TIMESTAMP:
                current[k] = datetime.now(timezone.utc)
            else:
                current[k] = v
        self.store[path] = current
