import os
from typing import Any

import msal
from dotenv import load_dotenv


load_dotenv()

SCOPES = ["https://graph.microsoft.com/.default"]


def get_access_token() -> Any:
    tenant_id = os.environ["AZ_TENANT_ID"]
    client_id = os.environ["AZ_CLIENT_ID"]
    client_secret = os.environ["AZ_CLIENT_SECRET"]

    authority = f"https://login.microsoftonline.com/{tenant_id}"

    app = msal.ConfidentialClientApplication(
        client_id=client_id,
        authority=authority,
        client_credential=client_secret,
    )

    result = app.acquire_token_for_client(scopes=SCOPES)

    return result["access_token"]
