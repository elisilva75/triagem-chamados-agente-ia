import asyncio

import httpx
import pytest

from scripts.us08_groq_pilot import PilotTransport
from tests.unit.test_openai_provider import no_external_network  # noqa: F401


@pytest.mark.parametrize("status", [200, 400, 429])
def test_pilot_transport_limits_and_errors(status):
    requests = []
    report = {"requests": []}

    def handler(request):
        requests.append(request)
        return httpx.Response(
            status,
            json={
                "usage": {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30},
                "error": {"code": "insufficient_quota", "message": "PRIVATE"},
            },
            headers={
                "x-request-id": "req_fake",
                "x-ratelimit-limit-tokens": "8000",
                "x-ratelimit-remaining-tokens": "PRIVATE",
            },
        )

    meter = PilotTransport(report, lambda: None, factory=lambda: httpx.MockTransport(handler))

    async def run():
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/responses")
        for _ in range(3 if status == 200 else 1):
            result = await meter.handle_async_request(request)
            assert result.status_code == status
        with pytest.raises(ConnectionError):
            await meter.handle_async_request(request)

    asyncio.run(run())
    assert len(requests) == (3 if status == 200 else 1)
    assert "PRIVATE" not in str(report)
    assert report["requests"][0]["rate_limits"] == {"x-ratelimit-limit-tokens": 8000}
    if status == 200:
        assert report["requests"][0]["usage"]["total_tokens"] == 30
    else:
        assert set(report["requests"][0]) == {
            "number",
            "status",
            "code",
            "request_id",
            "rate_limits",
        }


def test_timeout_stops_without_retry():
    requests = []

    def handler(request):
        requests.append(request)
        raise httpx.ReadTimeout("PRIVATE", request=request)

    report = {"requests": []}
    meter = PilotTransport(report, lambda: None, factory=lambda: httpx.MockTransport(handler))

    async def run():
        request = httpx.Request("POST", "https://api.groq.com/openai/v1/responses")
        with pytest.raises(httpx.ReadTimeout):
            await meter.handle_async_request(request)
        with pytest.raises(ConnectionError):
            await meter.handle_async_request(request)

    asyncio.run(run())
    assert len(requests) == 1
    assert "PRIVATE" not in str(report)
