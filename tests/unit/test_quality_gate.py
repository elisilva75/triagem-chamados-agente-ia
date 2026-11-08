from types import SimpleNamespace

import pytest

from scripts import check_quality


def test_pipeline_stops_on_first_failure(monkeypatch):
    monkeypatch.setenv("AI_MODE", "simulated")
    monkeypatch.setenv("TEST_DATABASE_URL", "isolated-test-placeholder")
    calls = []

    def fail(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=7)

    monkeypatch.setattr(check_quality.subprocess, "run", fail)
    assert check_quality.main() == 7
    assert len(calls) == 1


@pytest.mark.parametrize(
    "content", ["<testsuite/>", "<testsuite><testcase><skipped/></testcase></testsuite>"]
)
def test_required_report_rejects_empty_or_skipped(tmp_path, content):
    report = tmp_path / "results.xml"
    report.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        check_quality.complete_report(report)


def test_pipeline_requires_simulation_and_database(monkeypatch):
    monkeypatch.delenv("TEST_DATABASE_URL", raising=False)
    assert check_quality.main() == 2
