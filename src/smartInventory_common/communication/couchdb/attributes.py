from smartInventory_common.communication.couchdb import CouchDB
from smartInventory_common.utils.exceptions import AttributesNotFound, CouchDBSendError


class CouchDBAttributes(CouchDB):
    def __init__(self, parameters: dict, queryset=None):
        super(CouchDBAttributes, self).__init__(parameters)
        self.queryset = queryset

    @staticmethod
    def format_attributes(attributes) -> dict:
        formatted_attributes = {}
        for attribute in attributes:
            if isinstance(attribute["name"], str):
                formatted_attributes[attribute["name"]] = attribute["value"]
            else:
                formatted_attributes[attribute["name"].name] = attribute["value"]

        return formatted_attributes

    def create_attributes(self, attributes):
        # Create instance attributes
        formatted_attributes = self.format_attributes(attributes)
        response, status_code = self.send_data("POST", "", formatted_attributes)

        if status_code != 201:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)
        return response["id"]

    def get_document(self, document_id):
        response, status_code = self.request("GET", document_id)
        if status_code != 200:
            print("error couchdb", response)
            raise AttributesNotFound(detail=response)
        return response

    def format_attributes_array(self, attributes: dict):
        formatted_array = []

        for key, value in attributes.items():
            if key in ["_id", "_rev"]:
                """Internal fields"""
                continue
            if self.queryset is None:
                formatted_array.append({"name": key, "value": value})
            else:
                attribute = self.queryset.objects.get(name=key)

                formatted_array.append({"id": attribute, "name": key, "value": value})

        return formatted_array

    def get_attributes(self, attributes_id):
        if not attributes_id:
            return []
        attributes = self.get_document(attributes_id)
        return self.format_attributes_array(attributes)

    def delete_attributes(self, attributes_id):
        attributes = self.get_document(attributes_id)

        response, status_code = self.request("DELETE", attributes_id + "?rev=" + attributes["_rev"])
        if status_code != 200 and status_code != 202:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)

    def update_attribute(self, attributes_id, attributes):
        formatted_attributes = self.format_attributes(attributes)
        attributes = self.get_document(attributes_id)

        response, status_code = self.send_data(
            "PUT", attributes_id + "?rev=" + attributes["_rev"], formatted_attributes
        )

        if status_code != 201 and status_code != 202:
            print("Error Couchdb : ", response)
            raise CouchDBSendError(detail=response)

        return response["id"]

    def find_attribute(self, key, value=None):
        if value:
            search_query = {"selector": {key: {"$eq": value}}}
        else:
            search_query = {"selector": {key: {"$exists": True}}}

        response, status_code = self.send_data("POST", "_find", search_query)

        if status_code != 200:
            print("Error Couchdb : ", response)
            if status_code == 404:
                return None
            raise CouchDBSendError(detail=response)
        return response
