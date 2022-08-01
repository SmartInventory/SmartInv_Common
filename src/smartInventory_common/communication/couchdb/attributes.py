from django.conf import settings
from smartInventory_common.utils.exceptions import AttributesNotFound, CouchDBSendError


class CouchDBAttributes:
    queryset = None

    @staticmethod
    def format_attributes(attributes) -> dict:
        formatted_attributes = {}
        for attribute in attributes:
            if "attributes_id" in attribute:
                formatted_attributes[attribute["attribute_id"].name] = attribute["value"]
            else:
                formatted_attributes[attribute["name"]] = attribute["value"]
        return formatted_attributes

    @classmethod
    def create_attributes(cls, attributes):
        # Create instance attributes
        formatted_attributes = cls.format_attributes(attributes)
        response, status_code = settings.COUCHDB_CONNECTION.send_data("POST", "", formatted_attributes)

        if status_code != 201:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)
        return response["id"]

    @classmethod
    def get_document(cls, document_id):
        response, status_code = settings.COUCHDB_CONNECTION.request("GET", document_id)
        if status_code != 200:
            print("error couchdb", response)
            raise AttributesNotFound(detail=response)
        return response

    @classmethod
    def format_attributes_array(cls, attributes: dict):
        formatted_array = []

        for key, value in attributes.items():
            if key in ["_id", "_rev"]:
                """Internal fields"""
                continue
            if cls.queryset is None:
                formatted_array.append({"name": key, "value": value})
            else:
                attribute = cls.queryset.objects.get(name=key)

                formatted_array.append({"attribute_id": attribute, "name": key, "value": value})

        return formatted_array

    @classmethod
    def get_attributes(cls, attributes_id):
        if not attributes_id:
            return []
        attributes = cls.get_document(attributes_id)
        return cls.format_attributes_array(attributes)

    @classmethod
    def delete_attributes(cls, attributes_id):
        attributes = cls.get_document(attributes_id)

        response, status_code = settings.COUCHDB_CONNECTION.request(
            "DELETE", attributes_id + "?rev=" + attributes["_rev"]
        )
        if status_code != 200 and status_code != 202:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)

    @classmethod
    def update_attribute(cls, attributes_id, attributes):
        formatted_attributes = cls.format_attributes(attributes)
        attributes = cls.get_document(attributes_id)

        response, status_code = settings.COUCHDB_CONNECTION.send_data(
            "PUT", attributes_id + "?rev=" + attributes["_rev"], formatted_attributes
        )

        if status_code != 201 and status_code != 202:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)

        return response["id"]
