from rest_framework import pagination


class CustomPageNumberPagination(pagination.PageNumberPagination):
    page_size_query_param = "size"

    def get_next_link(self):
        if not self.page.has_next():
            return None
        return self.page.next_page_number()

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        return self.page.previous_page_number()

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "required": ["count", "results"],
            "properties": {
                "count": {
                    "type": "integer",
                    "example": 123,
                },
                "next": {"type": "integer", "nullable": True, "example": 2},
                "previous": {"type": "integer", "nullable": True, "example": 1},
                "results": schema,
            },
        }
