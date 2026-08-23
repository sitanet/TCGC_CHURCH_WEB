"""
Custom REST Framework pagination and response wrappers.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination style for The CityGate Church API.
    Provides total pages, current page, and record counts.
    """
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "pagination": {
                "count": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
            },
            "results": data,
        })
