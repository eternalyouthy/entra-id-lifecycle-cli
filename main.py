import time
import requests

from auth import get_access_token
from graph_client import GraphClient


token = get_access_token()
graph = GraphClient(token)

# Retrieving the list of users
data = graph.get(
    "/users",
    params={
        "$select": "displayName,userPrincipalName,department",
    },
)

for user in data["value"]:
    print(
        user["displayName"],
        "|",
        user.get("department"),
    )

target_upn = "dmitri.wolf@randompc13556outlook.onmicrosoft.com"

# 1. Retrieve a specific user
user = graph.get(
    f"/users/{target_upn}",
    params={
        "$select": "id,displayName,userPrincipalName",
    },
)

# Extract the user's string ID.
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

# Verification: the duration of a person's time in the group exceeds this figure.
r = requests.get(
    f"https://graph.microsoft.com/v1.0/users/{user_id}/memberOf",
    headers={"Authorization": f"Bearer {token}"},
)
r.raise_for_status()
remaining = [g.get("displayName") for g in r.json()["value"]]
print("Remaining in the groups:", remaining)
assert "sec-all-employees" not in remaining

# 6. Soft-delete user's
"""r = requests.delete(
    f"https://graph.microsoft.com/v1.0/users/{user_id}",
    headers={"Authorization": f"Bearer {token}"},
)
print("Soft-delete:", r.status_code)  # waiting 204"""

# User deletion is intentionally disabled for safety reasons
print("Soft-delete: DISABLED (safety reasons)")


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
