from datetime import datetime, timedelta

import pytest

from logs.authentication_logs import NiboAuthError
from src.config import NiboRoutes
from src.nibo_client import RouteRequest

SCHEDULED_ROUTES = {NiboRoutes.CONTAS_A_PAGAR, NiboRoutes.CONTAS_A_RECEBER}
HISTORICAL_ROUTES = {NiboRoutes.CONTAS_RECEBIDAS, NiboRoutes.CONTAS_PAGAS}


def mock_all_routes(requests_mock, json_body=None):
    """Registers a mocked response for all 4 real NiboRoutes."""
    body = json_body if json_body is not None else {}
    for route in NiboRoutes:
        requests_mock.get(route.value, json=body, status_code=200)


def test_instance_loads_token_for_eva_clinica():
    client = RouteRequest("eva clinica")
    assert client.api_token == "token-fake-eva-clinica"
    assert len(client.routes) == 4


def test_instance_loads_token_for_dr_mikle():
    client = RouteRequest("dr mikle")
    assert client.api_token == "token-fake-dr-mikle"


def test_unknown_client_raises_key_error():
    with pytest.raises(KeyError):
        RouteRequest("unknown_client")


def test_routes_requests_returns_one_response_per_route(requests_mock):
    mock_all_routes(requests_mock, json_body={"contas": []})

    client = RouteRequest("eva clinica")
    result = client.routes_requests()

    assert isinstance(result, list)
    assert len(result) == 4


def test_sends_apitoken_header_on_every_request(requests_mock):
    mock_all_routes(requests_mock)

    client = RouteRequest("eva clinica")
    client.routes_requests()

    assert len(requests_mock.request_history) == 4
    for req in requests_mock.request_history:
        assert req.headers["ApiToken"] == "token-fake-eva-clinica"


def test_scheduled_routes_use_future_date_filter(requests_mock):
    """CONTAS_A_PAGAR and CONTAS_A_RECEBER (name contains '_A_') should
    filter from today up to +7 days - these are not-yet-due items."""
    mock_all_routes(requests_mock)

    client = RouteRequest("eva clinica")
    client.routes_requests()

    today = datetime.now().strftime("%Y-%m-%d")
    seven_days_ahead = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

    scheduled_urls = {route.value for route in SCHEDULED_ROUTES}
    scheduled_requests = [
        req for req in requests_mock.request_history
        if req.url.split("?")[0] in scheduled_urls
    ]

    assert len(scheduled_requests) == 2
    for req in scheduled_requests:
        filter_param = req.qs.get("$filter", [""])[0]
        assert today in filter_param
        assert seven_days_ahead in filter_param


def test_historical_routes_use_past_date_filter(requests_mock):
    """CONTAS_RECEBIDAS and CONTAS_PAGAS (no '_A_' in the name) should
    filter from -7 days up to today - these are already settled items."""
    mock_all_routes(requests_mock)

    client = RouteRequest("eva clinica")
    client.routes_requests()

    today = datetime.now().strftime("%Y-%m-%d")
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    historical_urls = {route.value for route in HISTORICAL_ROUTES}
    historical_requests = [
        req for req in requests_mock.request_history
        if req.url.split("?")[0] in historical_urls
    ]

    assert len(historical_requests) == 2
    for req in historical_requests:
        filter_param = req.qs.get("$filter", [""])[0]
        assert seven_days_ago in filter_param
        assert today in filter_param


def test_api_error_response_raises_auth_error(requests_mock):
    """A 401 from NIBO must raise NiboAuthError instead of being appended
    to the result as if it were valid data (backlog US2.5)."""
    for route in NiboRoutes:
        if route == NiboRoutes.CONTAS_A_PAGAR:
            requests_mock.get(route.value, json={"error": "unauthorized"}, status_code=401)
        else:
            requests_mock.get(route.value, json={}, status_code=200)

    client = RouteRequest("eva clinica")

    with pytest.raises(NiboAuthError):
        client.routes_requests()