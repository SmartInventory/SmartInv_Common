import json
from dataclasses import dataclass

import requests
from django.core.cache import cache
from requests import Response

from rest_framework import serializers


@dataclass
class RequestsBackend:
    route = None
    serializer = None
    service_url = None

    def __init__(self):
        if not self.serializer or not self.route or not self.service_url:
            raise NotImplementedError

    def get_cache_or_live(self, component_id):
        """
        Get from cache or from backend
        :param component_id:
        :return:
        """

        cache_comp = cache.get(f"{self.route}_{component_id}")

        if cache_comp:
            print("HIT¡")
            serializer = self.serializer(data=json.loads(cache_comp))
            serializer.is_valid(raise_exception=True)
            return serializer

        print("MISS")
        response = self.get(component_id)
        if response.status_code == 200:
            serializer = self.serializer(data=response.json())
            if serializer.is_valid():
                cache.set(f"{self.route}_{component_id}", response.text)
                return serializer
        return self.handle_error(response)

    def get(self, path: str):
        if path:
            url = self.service_url + "/api" + self.route + "/" + path + "/?format=json"
        else:
            url = self.service_url + "/api" + self.route + "/?format=json"
        return requests.request(
            "GET",
            url,
            headers={"Accept": "application/json"},
        )

    @staticmethod
    def handle_error(response: Response):
        try:
            raise serializers.ValidationError(response.json())
        except (TypeError, requests.exceptions.JSONDecodeError):
            raise serializers.ValidationError(response.content)

    def get_component_model(self, component_id) -> any:
        """
            Get component model from backend
        :param component_id:
        :return:
        """

        serializer = self.get_cache_or_live(component_id)
        if serializer.is_valid(raise_exception=True):
            return serializer
        raise ValueError(serializer.errors)

    def post_data(self, data, path=None, method="POST") -> Response:
        """
        Send data
        :param path:
        :param method:
        :param data:
        :return:
        """
        if path:
            url = self.service_url + "/api" + self.route + "/" + path + "/"
        else:
            url = self.service_url + "/api" + self.route + "/"

        return requests.request(method, url, headers={"Accept": "application/json"}, data=data)
