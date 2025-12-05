from django.http import HttpRequest


class AccessFilterMixin:
    def filter_by_access(
        self,
        request: HttpRequest,
        access_defaults=(None, None, None, None),
    ):
        """Filter queryset by what the active request user has access to before anything else.

        Args:
            request (Request): Current active request. If not actively in a request, then use [all()] like you normally would
            access_defaults ((Bool|None, Bool|None, Bool|None, Bool|None), True): CRUD permissions to filter against. Defaults to *all*

        Returns:
            (QuerySet): returns model queryset
        """
        assert (
            len(access_defaults) == 4
        ), "(C,R,U,D) values required, fuzzy matches `None` values"
        access_filters = {}
        if access_defaults[0] is not None:
            access_filters["can_create"] = access_defaults[0]
        if access_defaults[1] is not None:
            access_filters["can_read"] = access_defaults[1]
        if access_defaults[2] is not None:
            access_filters["can_update"] = access_defaults[2]
        if access_defaults[3] is not None:
            access_filters["can_delete"] = access_defaults[3]

        print(access_filters)
        return self.get_queryset().filter()
