from rest_framework.exceptions import APIException


class CouchDBSendError(APIException):
    status_code = 500
    default_detail = "Can´t send data to CouchDB"
    default_code = "error.couchdb.send"


class AttributesNotFound(APIException):
    status_code = 404
    default_detail = "attributes_id not found in CouchDB"
    default_code = "error.attributes.not_found"
