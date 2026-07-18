import os
import msal
from dotenv import load_dotenv


load_dotenv()

SCOPES = ["https://graph.microsoft.com/.default"]


def get_access_token() -> str:
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

    if "access_token" not in result:
        raise RuntimeError(
            f"Не удалось получить токен: {result.get('error')} — "
            f"{result.get('error_description')}"
        )

    return result["access_token"]
