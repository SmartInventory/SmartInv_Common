import json
import requests
from django.conf import settings
from django.core.cache import cache
from requests import Response

from rest_framework import serializers

BACKEND_REQ_TEST_VARIABLES = {
    "model_id_not_found": "7a35a50b-bb76-432d-8c62-5b7ea1ad0af8",
    "attribute_id_not_found": "350efcc4-62a5-4c09-81cc-e5af4366c705",
    "model_id_wo_attrs": "e2340d6c-622a-41ae-8939-a53c79a1bed0",
}


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

        if settings.TESTING:
            if component_id == BACKEND_REQ_TEST_VARIABLES["model_id_not_found"]:
                raise serializers.ValidationError({"error": "error.equipment_model.not_found"})
            if component_id == BACKEND_REQ_TEST_VARIABLES["attribute_id_not_found"]:
                raise serializers.ValidationError({"error": "error.equipment_attribute.not_found"})
            if cls.route == "/equipment_model":
                fake_data = {
                    "id": str(component_id),
                    "reference": "28bc52f7f13e4bbf841d8729141267f3",
                    "quantity": 0,
                    "name": "Cisco 2900 series",
                    "description": "A Cisco 2900 series router",
                    "borrow_type": "IL",
                    "needs_guarantor": True,
                    "attributes": [{"id": "3afbd088-3076-4edf-b36e-0e175dd9d752", "value": "2009"}],
                    "attributes_id": "4f5fb3b57c5263054ecab57c88035a12",
                }
                if component_id == BACKEND_REQ_TEST_VARIABLES["model_id_wo_attrs"]:
                    fake_data["attributes"] = []
                serializer = cls.serializer(data=fake_data)
                serializer.is_valid(raise_exception=True)
                return serializer
            elif cls.route == "/equipment_attribute":
                fake_data = {"id": str(component_id), "name": "ATTR" + str(component_id), "description": ""}
                serializer = cls.serializer(data=fake_data)
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
