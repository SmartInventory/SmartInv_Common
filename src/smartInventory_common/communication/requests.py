import hashlib
import json
import requests
from django.conf import settings
from django.core.cache import cache
from requests import Response

from rest_framework import serializers

from smartInventory_common.utils import common_logger

module_logger = common_logger.getChild("RequestsBackend")

BACKEND_REQ_TEST_VARIABLES = {
    "model_id_not_found": "7a35a50b-bb76-432d-8c62-5b7ea1ad0af8",
    "attribute_id_not_found": "350efcc4-62a5-4c09-81cc-e5af4366c705",
    "model_id_wo_attrs": "e2340d6c-622a-41ae-8939-a53c79a1bed0",
    "attribute_supervalue": "supervalue",
    "lab_not_found": "56746edd-eefa-4a4c-a68c-83369aed81f9",
}


class RequestsBackend:
    route = None
    serializer = None
    service_url = None

    def __init__(self):
        if not self.serializer or not self.route or not self.service_url:
            raise NotImplementedError

    @staticmethod
    def get_cache_key(route, component_id):
        return hashlib.md5(str(f"{route}_{component_id}").encode("UTF-8")).hexdigest()

    @classmethod
    def get_test_datas(cls, component_id, search=False):
        if component_id == BACKEND_REQ_TEST_VARIABLES["model_id_not_found"]:
            raise serializers.ValidationError({"error": "error.equipment_model.not_found"})
        elif component_id == BACKEND_REQ_TEST_VARIABLES["attribute_id_not_found"]:
            raise serializers.ValidationError({"error": "error.equipment_attribute.not_found"})
        elif component_id == BACKEND_REQ_TEST_VARIABLES["lab_not_found"]:
            raise serializers.ValidationError({"error": "error.laboratory.not_found"})
        elif cls.route == "/equipment_model":
            fake_data = {
                "id": "06646868-917e-4f4e-bdfe-0610ae592380" if search else str(component_id),
                "reference": "28bc52f7f13e4bbf841d8729141267f3",
                "quantity": 0,
                "name": "Cisco 2900 series",
                "description": "A Cisco 2900 series router",
                "borrow_type": "IL",
                "needs_guarantor": True,
                "attributes": [{"name": "testing", "value": "2009"}],
                "attributes_id": "4f5fb3b57c5263054ecab57c88035a12",
            }
            if component_id == BACKEND_REQ_TEST_VARIABLES["model_id_wo_attrs"]:
                fake_data["attributes"] = []
            serializer = cls.serializer(data=[fake_data] if search else fake_data, many=search)
            serializer.is_valid(raise_exception=True)
            return serializer
        elif cls.route == "/equipment_attribute":
            fake_data = {"name": "ATTR" + ("3afbd" if search else str(component_id)), "description": ""}
            if component_id == BACKEND_REQ_TEST_VARIABLES["attribute_supervalue"]:
                fake_data = {"name": "ATTRsupervalue", "description": ""}
            serializer = cls.serializer(data=fake_data, many=search)
            serializer.is_valid(raise_exception=True)
            return serializer
        elif cls.route == "/laboratory":

            fake_data = {"name": "Laboratory" + str(component_id)}
            serializer = cls.serializer(data=fake_data)
            serializer.is_valid(raise_exception=True)
            return serializer

    @classmethod
    def get_cache_or_live(cls, component_id, search=False):
        """
        Get from cache or from backend
        :param component_id:
        :return:
        """

        cache_comp = cache.get(cls.get_cache_key(cls.route, component_id))

        if cache_comp:
            module_logger.info("Cache : Hit!")
            serializer = cls.serializer(
                data=cache_comp if isinstance(cache_comp, dict) else json.loads(cache_comp), many=search
            )
            serializer.is_valid(raise_exception=True)
            return serializer

        module_logger.info("Cache : Miss")
        response = cls.get(component_id, search)
        if response.status_code == 200:
            if search:
                """If its a search"""
                serializer = cls.serializer(data=response.json()["results"], many=True)
            else:
                serializer = cls.serializer(data=response.json())
            if serializer.is_valid():
                cache.set(cls.get_cache_key(cls.route, component_id), json.dumps(serializer.data))
                return serializer
        return cls.handle_error(response)

    @classmethod
    def get(cls, path: str, search=False):
        if search:
            url = cls.service_url + "/api" + cls.route + "/" + path
        elif path:
            url = cls.service_url + "/api" + cls.route + "/" + path + "/?format=json"
        else:
            url = cls.service_url + "/api" + cls.route + "/?format=json"
        return requests.request(
            "GET",
            url,
            headers={"Accept": "application/json"},
        )

    @classmethod
    def remove_cache(cls, component_id):
        cache.delete(cls.get_cache_key(cls.route, component_id))

    @staticmethod
    def handle_error(response: Response):
        try:
            raise serializers.ValidationError(response.json())
        except (TypeError, requests.exceptions.JSONDecodeError):
            raise serializers.ValidationError(response.content)

    @classmethod
    def get_component_model(cls, component_id, search=False) -> any:
        """
            Get component model from backend
        :param search:
        :param component_id:
        :return:
        """
        if hasattr(settings, "TESTING"):
            serializer = cls.get_test_datas(str(component_id), search)
        else:
            serializer = cls.get_cache_or_live(str(component_id), search)
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
