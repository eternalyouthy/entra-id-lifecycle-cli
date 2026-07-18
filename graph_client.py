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

    def _build_url(self, endpoint):
        if endpoint.startswith("https://"):
            return endpoint

        return f"{self.BASE_URL}/{endpoint.lstrip('/')}"

    def get(self, endpoint, params=None):
        url = self._build_url(endpoint)

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()

    def patch(self, endpoint, json=None):
        url = self._build_url(endpoint)

        response = self.session.patch(
            url,
            json=json,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response

    def post(self, endpoint, json=None):
        url = self._build_url(endpoint)

        response = self.session.post(
            url,
            json=json,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response

    def delete(self, endpoint):
        url = self._build_url(endpoint)

        response = self.session.delete(
            url,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response
