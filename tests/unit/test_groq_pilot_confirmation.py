import json
from datetime import date, timedelta

import pytest

from scripts import us08_groq_pilot as pilot
from scripts.us08_confirmation import SINGLE_PILOT_SCOPE


def current_confirmation():
    return {
        "plan": "Livre",
        "active": True,
        "checked_on": date.today().isoformat(),
        "expires_on": (date.today() + timedelta(days=1)).isoformat(),
        "scope": SINGLE_PILOT_SCOPE,
    }


@pytest.mark.parametrize(
    "change",
    [
        None,
        {"plan": "Paid"},
        {"active": False},
        {"active": "true"},
        {"checked_on": (date.today() - timedelta(days=1)).isoformat()},
        {"expires_on": date.today().isoformat()},
        {"expires_on": (date.today() - timedelta(days=1)).isoformat()},
        {"scope": "AV08_once_revised"},
        {"scope": None},
        {"expires_on": "invalid"},
    ],
)
def test_standalone_confirmation_rejected_before_key_database_or_transport(
    tmp_path, monkeypatch, change
):
    def forbidden(*args, **kwargs):
        pytest.fail("Não pode ler chave/criar banco/enviar sem confirmação válida.")

    for name in ("dotenv_values", "create_engine", "GroqProvider"):
        monkeypatch.setattr(pilot, name, forbidden)
    monkeypatch.setattr(pilot, "REPORT", tmp_path / "not-created" / "report.json")
    confirmation = None if change is None else {**current_confirmation(), **change}
    with pytest.raises(ValueError):
        pilot.execute(confirmation=confirmation)
    assert not pilot.REPORT.parent.exists()

    if change is None:
        args = ["--execute-approved"]
    else:
        path = tmp_path / "confirmation.json"
        path.write_text(json.dumps(confirmation), encoding="utf-8")
        args = ["--execute-approved", "--confirmation", str(path)]
    monkeypatch.setattr(pilot, "execute", forbidden)
    with pytest.raises(SystemExit) as exc:
        pilot.main(args)
    assert exc.value.code == 2
    assert not pilot.REPORT.parent.exists()


def test_missing_confirmation_file_is_not_an_authorization(tmp_path, monkeypatch):
    monkeypatch.setattr(pilot, "execute", lambda **kwargs: pytest.fail("Sem autorização"))
    with pytest.raises(SystemExit) as exc:
        pilot.main(["--execute-approved", "--confirmation", str(tmp_path / "absent.json")])
    assert exc.value.code == 2
