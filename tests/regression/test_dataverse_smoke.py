"""Authenticated smoke checks for the deployed Dataverse UAT environment."""

import os
from urllib.parse import urlparse

import pytest
import requests


@pytest.fixture(scope="session")
def dataverse_session():
    environment_url = os.environ.get("UAT_URL", "").rstrip("/")
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")

    parsed_url = urlparse(environment_url)
    if parsed_url.scheme != "https" or not parsed_url.netloc or parsed_url.path:
        pytest.fail("UAT_URL must be an HTTPS Dataverse organization URL without a path.")
    if not tenant_id or not client_id or not client_secret:
        pytest.fail(
            "Set AZURE_TENANT_ID, AZURE_CLIENT_ID, and AZURE_CLIENT_SECRET "
            "to run authenticated UAT smoke checks."
        )

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_response = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
            "scope": f"{environment_url}/.default",
        },
        timeout=30,
    )
    if not token_response.ok:
        pytest.fail(
            "Dataverse token request failed "
            f"(HTTP {token_response.status_code}); verify the app registration "
            "and tenant consent."
        )

    access_token = token_response.json().get("access_token")
    if not access_token:
        pytest.fail("The identity provider response did not include an access token.")

    session = requests.Session()
    session.headers.update(
        {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "OData-Version": "4.0",
            "OData-MaxVersion": "4.0",
        }
    )
    return environment_url, session


def test_dataverse_whoami_is_available(dataverse_session):
    environment_url, session = dataverse_session
    response = session.get(
        f"{environment_url}/api/data/v9.2/WhoAmI",
        timeout=30,
    )

    assert response.status_code == 200, (
        f"Dataverse WhoAmI returned HTTP {response.status_code}; "
        "check the application user's environment access and security role."
    )
    assert response.json().get("UserId"), "Dataverse WhoAmI did not return a UserId."


def test_customer_service_solution_is_installed(dataverse_session):
    environment_url, session = dataverse_session
    solution_name = os.environ.get("SOLUTION_UNIQUE_NAME", "CustomerServiceDemo")
    response = session.get(
        f"{environment_url}/api/data/v9.2/solutions",
        params={
            "$select": "uniquename,version",
            "$filter": f"uniquename eq '{solution_name}'",
        },
        timeout=30,
    )

    assert response.status_code == 200, (
        f"Dataverse solution query returned HTTP {response.status_code}; "
        "check the application user's solution read permission."
    )
    solutions = response.json().get("value", [])
    assert any(solution.get("uniquename") == solution_name for solution in solutions), (
        f"Solution '{solution_name}' is not installed in {environment_url}."
    )
