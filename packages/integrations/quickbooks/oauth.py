"""QuickBooks Online OAuth 2.0 helpers."""
from __future__ import annotations

import base64
import os
from urllib.parse import urlencode

import httpx

QBO_AUTH_URL = "https://appcenter.intuit.com/connect/oauth2"
QBO_TOKEN_URL = "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer"
QBO_REVOKE_URL = "https://developer.api.intuit.com/v2/oauth2/tokens/revoke"

SCOPES = "com.intuit.quickbooks.accounting"

CLIENT_ID = os.getenv("QBO_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("QBO_CLIENT_SECRET", "")


def get_auth_url(redirect_uri: str, state: str) -> str:
    """Build the QBO OAuth2 authorization URL."""
    params = {
        "client_id": CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": SCOPES,
        "state": state,
    }
    return f"{QBO_AUTH_URL}?{urlencode(params)}"


async def exchange_code(code: str, redirect_uri: str, realm_id: str) -> dict:
    """Exchange auth code for access/refresh tokens."""
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            QBO_TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Basic {creds}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri,
            },
        )
        resp.raise_for_status()
        data = resp.json()
    return {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "realm_id": realm_id,
        "token_type": data.get("token_type", "bearer"),
        "expires_in": data.get("expires_in", 3600),
        "x_refresh_token_expires_in": data.get("x_refresh_token_expires_in", 8726400),
    }


async def refresh_token(refresh_tok: str) -> dict:
    """Refresh the access token using a refresh token."""
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            QBO_TOKEN_URL,
            headers={
                "Accept": "application/json",
                "Authorization": f"Basic {creds}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={"grant_type": "refresh_token", "refresh_token": refresh_tok},
        )
        resp.raise_for_status()
        return resp.json()


async def revoke_token(token: str) -> None:
    creds = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient() as client:
        await client.post(
            QBO_REVOKE_URL,
            headers={"Authorization": f"Basic {creds}", "Content-Type": "application/json"},
            json={"token": token},
        )
