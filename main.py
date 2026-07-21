import time

from auth import get_access_token
from graph_client import GraphClient


def offboard_user(graph, selected_user):
    user_id = selected_user["id"]

    print(f"Starting offboarding for {selected_user['displayName']} | id={user_id}")

    r = graph.patch(
        f"/users/{user_id}",
        json={"accountEnabled": False},
    )

    print("Disable:", r.status_code)  # waiting 204 No Content

    response = graph.post(
        f"/users/{user_id}/revokeSignInSessions",
    )

    print("Revoke sessions:", response.status_code)  # 200, body — {"value": true}

    data = graph.get(
        f"/users/{user_id}/memberOf",
    )

    groups = data["value"]

    group_id = next(
        (
            group["id"]
            for group in groups
            if group.get("displayName") == "sec-all-employees"
        ),
        None,
    )

    return user_id, group_id

    for group in groups:
        print("Group:", group.get("displayName"), group.get("id"))


token = get_access_token()
graph = GraphClient(token)

# Retrieving the list of users
data = graph.get(
    "/users",
    params={
        "$select": "id,displayName,userPrincipalName,department",
    },
)

users = data["value"]

for number, user in enumerate(users, start=1):
    print(
        number,
        "|",
        user["displayName"],
        "|",
        user["userPrincipalName"],
        "|",
        user.get("department"),
    )

error_message = f"Enter a whole number from 1 to {len(users)}."

while True:
    choice = input("\nChoose user number: ")

    try:
        choice_number = int(choice)
    except ValueError:
        print(error_message)
        continue

    if 1 <= choice_number <= len(users):
        break

    print(error_message)

choice_index = choice_number - 1
selected_user = users[choice_index]

print("Selected user ID:", selected_user["id"])

print(
    "Selected:",
    selected_user["displayName"],
    "|",
    selected_user["userPrincipalName"],
)

confirmation = input(
    f"\nType OFFBOARD to continue with {selected_user['displayName']}: "
)

if confirmation.strip().upper() != "OFFBOARD":
    print("Operation cancelled.")
    raise SystemExit

print("Confirmation accepted. Starting offboarding.")

# Run the offboarding workflow
user_id, group_id = offboard_user(graph, selected_user)

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
