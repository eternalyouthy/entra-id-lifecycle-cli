import os
from dotenv import load_dotenv
import requests

load_dotenv()

TENANT = os.environ["AZ_TENANT_ID"]
CLIENT_ID = os.environ["AZ_CLIENT_ID"]
SECRET = os.environ["AZ_CLIENT_SECRET"]

resp = requests.post(
    f"https://login.microsoftonline.com/{TENANT}/oauth2/v2.0/token",
    data={
        "client_id": CLIENT_ID,
        "client_secret": SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials",
    },
)
resp.raise_for_status()
token = resp.json()["access_token"]

r = requests.get(
    "https://graph.microsoft.com/v1.0/users?$select=displayName,userPrincipalName,department",
    headers={"Authorization": f"Bearer {token}"},
)
print(r.status_code)
for u in r.json()["value"]:
    print(u["displayName"], "|", u.get("department"))

target_upn = "dmitri.wolf@randompc13556outlook.onmicrosoft.com"

# 1. Найти объект пользователя и его ID
r = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{target_upn}",
    headers={"Authorization": f"Bearer {token}"},
)
r.raise_for_status()
user = r.json()
user_id = user["id"]
print(f"Найден: {user['displayName']} | id={user_id}")

# 2. Disable account
r = requests.patch(
    f"https://graph.microsoft.com/v1.0/users/{user_id}",
    headers={"Authorization": f"Bearer {token}"},
    json={"accountEnabled": False},
)
print("Disable:", r.status_code)  # ожидаем 204 No Content

# 3. Revoke sign-in sessions
r = requests.post(
    f"https://graph.microsoft.com/v1.0/users/{user_id}/revokeSignInSessions",
    headers={"Authorization": f"Bearer {token}"},
)
print("Revoke sessions:", r.status_code)  # 200, тело — {"value": true}

# 4. Посмотреть, в каких группах он состоит
r = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf",
    headers={"Authorization": f"Bearer {token}"},
)
r.raise_for_status()
groups = r.json()["value"]
for g in groups:
    print("Группа:", g.get("displayName"), g.get("id"))