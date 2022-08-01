from rest_framework.response import Response
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):

    page_size = 30

    def get_paginated_response(self, data):
        return Response(
            {
                "page_size": self.page_size,
                "next_page": self.page.next_page_number() if self.page.has_next() else None,
                "prev_page": self.page.previous_page_number() if self.page.has_previous() else None,
                "count": self.page.paginator.count,
                "results": data,
            }
        )
