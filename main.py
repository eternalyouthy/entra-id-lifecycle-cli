import time

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

print(f"Found: {user['displayName']} | id={user_id}")

# 2. Disable account
r = graph.patch(
    f"/users/{user_id}",
    json={"accountEnabled": False},
)
print("Disable:", r.status_code)  # waiting 204 No Content

# 3. Revoke sign-in sessions
r = graph.post(
    f"/users/{user_id}/revokeSignInSessions",
)
print("Revoke sessions:", r.status_code)  # 200, body — {"value": true}

# 4. See which groups he is a member of
data = graph.get(
    f"/users/{user_id}/memberOf",
)

groups = data["value"]

for g in groups:
    print("Group:", g.get("displayName"), g.get("id"))

# 5. Find the ID of the sec-all-employees group and remove the membership.
group_id = next(
    (g["id"] for g in groups if g.get("displayName") == "sec-all-employees"), None
)

if group_id:
    r = graph.delete(
        f"/groups/{group_id}/members/{user_id}/$ref",
    )
    print("Remove from group:", r.status_code)
else:
    print("No longer in sec-all-employees — skipping membership removal.")

# 6. Soft-delete user's
"""
r = graph.delete(
    f"/users/{user_id}",
)
print("Soft-delete:", r.status_code)  # Expected: 204 No Content
"""

# User deletion is intentionally disabled for safety reasons
print("Soft-delete: DISABLED (safety reasons)")


def wait_for_group_removal(
    graph,
    user_id,
    group_display_name,
    attempts=5,
    delay=3,
):
    for _ in range(attempts):
        data = graph.get(
            f"/users/{user_id}/memberOf",
        )

        remaining = [g.get("displayName") for g in data["value"]]

        if group_display_name not in remaining:
            return True

        time.sleep(delay)

    return False


if not wait_for_group_removal(
    graph,
    user_id,
    "sec-all-employees",
):
    print("Note: The change has not yet been replicated — check manually later.")
