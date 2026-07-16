import requests


class GraphClient:
    BASE_URL = "https://graph.microsoft.com/v1.0"

    def __init__(self, token, timeout=10):
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        )

    def get(self, endpoint, params=None):
        if endpoint.startswith("https://"):
            url = endpoint
        else:
            url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()
