import json

import requests
from django.core.cache import cache
from requests import Response

from rest_framework import serializers


class RequestsBackend:
    route = None
    serializer = None
    service_url = None

    def __init__(self):
        if not self.serializer or not self.route or not self.service_url:
            raise NotImplementedError

    @classmethod
    def get_cache_or_live(cls, component_id):
        """
        Get from cache or from backend
        :param component_id:
        :return:
        """

        cache_comp = cache.get(f"{cls.route}_{component_id}")

        if cache_comp:
            print("HIT¡")
            serializer = cls.serializer(data=json.loads(cache_comp))
            serializer.is_valid(raise_exception=True)
            return serializer

        print("MISS")
        response = cls.get(component_id)
        if response.status_code == 200:
            serializer = cls.serializer(data=response.json())
            if serializer.is_valid():
                cache.set(f"{cls.route}_{component_id}", response.text)
                return serializer
        return cls.handle_error(response)

    @classmethod
    def get(cls, path: str):
        if path:
            url = cls.service_url + "/api" + cls.route + "/" + path + "/?format=json"
        else:
            url = cls.service_url + "/api" + cls.route + "/?format=json"
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

    @classmethod
    def get_component_model(cls, component_id) -> any:
        """
            Get component model from backend
        :param component_id:
        :return:
        """

        serializer = cls.get_cache_or_live(component_id)
        if serializer.is_valid(raise_exception=True):
            return serializer
        raise ValueError(serializer.errors)

    @classmethod
    def post_data(cls, data, path=None, method="POST") -> Response:
        """
        Send data
        :param path:
        :param method:
        :param data:
        :return:
        """
        if path:
            url = cls.service_url + "/api" + cls.route + "/" + path + "/"
        else:
            url = cls.service_url + "/api" + cls.route + "/"

        return requests.request(method, url, headers={"Accept": "application/json"}, data=data)
