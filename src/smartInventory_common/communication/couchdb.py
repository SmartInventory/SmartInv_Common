import requests


class CouchDB:
    def __init__(self, parameters: dict):
        self.credentials = (parameters["USERNAME"], parameters["PASSWORD"])

        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

        self.url = parameters["URL"]
        self.name = parameters["NAME"]

    def request(
        self, method: str, path: str
    ) -> (dict, int,):
        response = requests.request(
            method, f"{self.url}/{self.name}/{path}", headers=self.headers, auth=self.credentials
        )

        return (
            response.json(),
            response.status_code,
        )

    def send_data(
        self, method: str, path: str, payload: dict
    ) -> (dict, int,):
        response = requests.request(
            method, f"{self.url}/{self.name}/{path}", headers=self.headers, auth=self.credentials, json=payload
        )

        return (
            response.json(),
            response.status_code,
        )
