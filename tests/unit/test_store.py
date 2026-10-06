import json
import time

import pytest

from mlca.errors import IntegrityError
from mlca.log.store import Store


def seed(store):
    store.append(
        "ProjectCreated",
        {
            "project_id": "test",
            "mlca_version": "test",
            "template_id": "test",
            "template_version": "test",
            "template_sha256": "test",
        },
    )


def edit_line(store, number):
    lines = store.path.read_text().splitlines()
    record = json.loads(lines[number - 1])
    record["payload"]["text"] = "EDIT" if record["type"] == "Note" else record["payload"].get("text", "")
    lines[number - 1] = json.dumps(record, separators=(",", ":"))
    store.path.write_text("\n".join(lines) + "\n")


def test_incremental_read_and_hash_chain(tmp_path, monkeypatch):
    store = Store(tmp_path)
    seed(store)
    store.read()
    monkeypatch.setattr(store, "_read", lambda: pytest.fail("Unexpected full log reread"))
    store.append("Note", {"text": "one"})
    assert len(store.read()) == 2
    other = Store(tmp_path)
    other.append("Note", {"text": "two"})
    assert len(store.read()) == 3
    assert store.read()[-1].prev_hash


@pytest.mark.parametrize("last", [False, True])
def test_tamper_messages(tmp_path, last):
    store = Store(tmp_path)
    seed(store)
    store.append("Note", {"text": "original"})
    store.append("Note", {"text": "last"})
    store.read()
    edit_line(store, 3 if last else 2)
    message = (
        r"last line \(3\) was modified or truncated"
        if last
        else r"line 2 was modified \(its hash no longer matches line 3\)"
    )
    with pytest.raises(IntegrityError, match=message):
        store.verify()
    with pytest.raises(IntegrityError):
        Store(tmp_path).verify()


def test_truncation(tmp_path):
    store = Store(tmp_path)
    seed(store)
    store.append("Note", {"text": "second"})
    store.path.write_bytes(store.path.read_bytes().splitlines(keepends=True)[0])
    with pytest.raises(IntegrityError, match="modified or truncated"):
        store.read()


def test_5000_appends(tmp_path):
    store = Store(tmp_path)
    seed(store)
    started = time.monotonic()
    for index in range(5000):
        store.append("Note", {"text": str(index)})
    elapsed = time.monotonic() - started
    print(f"5000 appends: {elapsed:.3f}s")
    assert elapsed < 30
    assert store.verify()["records"] == 5001
