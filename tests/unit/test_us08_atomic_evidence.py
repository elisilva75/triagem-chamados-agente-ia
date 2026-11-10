import json

import pytest

from scripts import us08_groq_pilot as pilot


def denied(winerror):
    exc = PermissionError(13, "private")
    exc.winerror = winerror
    return exc


def test_transient_windows_denial_keeps_old_manifest_until_atomic_replace(tmp_path, monkeypatch):
    path = tmp_path / "manifest.json"
    path.write_text('{"old": true}', encoding="utf-8")
    original = type(path).replace
    received, delays = [], []

    def replace(temp, target):
        # Reabrir prova que a escrita terminou; nenhuma reescrita parcial do destino.
        assert json.loads(temp.read_text(encoding="utf-8")) == {"new": True}
        assert json.loads(path.read_text(encoding="utf-8")) == {"old": True}
        received.append(temp)
        if len(received) < 3:
            raise denied(5)
        return original(temp, target)

    monkeypatch.setattr(type(path), "replace", replace)
    monkeypatch.setattr(pilot.time, "sleep", delays.append)
    pilot.write_json(path, {"new": True})
    assert len(received) == 3 and delays == [0.01, 0.02]
    assert json.loads(path.read_text(encoding="utf-8")) == {"new": True}


@pytest.mark.parametrize("code,attempts", [(5, 5), (32, 5), (33, 5), (None, 1)])
def test_permanent_denial_is_bounded_and_preserves_previous_and_pending(
    tmp_path, monkeypatch, code, attempts
):
    path = tmp_path / "manifest.json"
    path.write_text('{"old": true}', encoding="utf-8")
    received, delays = [], []

    def replace(*args):
        received.append(args)
        raise denied(code)

    monkeypatch.setattr(type(path), "replace", replace)
    monkeypatch.setattr(pilot.time, "sleep", delays.append)
    with pytest.raises(PermissionError):
        pilot.write_json(path, {"new": True})
    assert len(received) == attempts
    assert sum(delays) <= 0.15 + 1e-9
    assert json.loads(path.read_text()) == {"old": True}
    assert json.loads(path.with_suffix(".tmp").read_text()) == {"new": True}
    assert "private" not in json.dumps(pilot.error_metadata(denied(code)))
