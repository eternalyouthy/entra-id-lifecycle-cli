import os
from dotenv import load_dotenv
import requests
import time

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

# 1. Find an object and his ID
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

# 4. See which groups he is a member of
r = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf",
    headers={"Authorization": f"Bearer {token}"},
)
r.raise_for_status()
groups = r.json()["value"]
for g in groups:
    print("Группа:", g.get("displayName"), g.get("id"))

# 5. Find the ID of the sec-all-employees group and remove the membership.
group_id = next(
    (g["id"] for g in groups if g.get("displayName") == "sec-all-employees"), None
)

if group_id:
    r = requests.delete(
        f"https://graph.microsoft.com/v1.0/groups/{group_id}/members/{user_id}/$ref",
        headers={"Authorization": f"Bearer {token}"},
    )
    print("Remove from group:", r.status_code)
else:
    print("No longer in sec-all-employees — skipping membership removal.")

# Проверка: юзер жив и в группе его больше нет
r = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf",
    headers={"Authorization": f"Bearer {token}"},
)
r.raise_for_status()
remaining = [g.get("displayName") for g in r.json()["value"]]
print("Remaining in the groups:", remaining)
assert "sec-all-employees" not in remaining

# 6. Soft-delete user's
r = requests.delete(
    f"https://graph.microsoft.com/v1.0/users/{user_id}",
    headers={"Authorization": f"Bearer {token}"},
)
print("Soft-delete:", r.status_code)  # waiting 204


def wait_for_group_removal(user_id, group_display_name, token, attempts=5, delay=3):
    for i in range(attempts):
        r = requests.get(
            f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf",
            headers={"Authorization": f"Bearer {token}"},
        )
        r.raise_for_status()
        remaining = [g.get("displayName") for g in r.json()["value"]]
        if group_display_name not in remaining:
            return True
        time.sleep(delay)
    return False


if not wait_for_group_removal(user_id, "sec-all-employees", token):
    print("Note: The change has not yet been replicated — check manually later.")
