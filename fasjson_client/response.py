class PaginationError(Exception):
    pass


class ResponseWrapper:
    """Wraps an operation to return our Response object.

    This avoids making the user go through the .response().result hoops.

    :type operation: :class:`bravado_core.operation.Operation`
    """

    def __init__(self, operation):
        self.operation = operation

    def __getattr__(self, name):
        """Forward requests for attrs not found on this decorator to the
        delegate.
        """
        return getattr(self.operation, name)

    def __call__(self, **kwargs):
        """Invoke the actual HTTP request and return a FASJSONResponse.

        :rtype: :class:`FASJSONResponse`
        """
        call_result = self.operation(**kwargs).response().result
        return FASJSONResponse(call_result, operation=self, operation_args=kwargs)


class FASJSONResponse:
    """Wraps an API response in a dict-like object.

    The object has methods and properties for pagination.
    """

    def __init__(self, response, operation, operation_args):
        self._response = response
        self._operation = operation
        self._operation_args = operation_args

    def __repr__(self):
        op_id = self._operation.operation.operation.operation_id
        op_args = ", ".join(
            ["{}={}".format(k, v) for k, v in self._operation_args.items()]
        )
        return "<{} for {}({})>".format(self.__class__.__name__, op_id, op_args)

    def __str__(self):
        return str(self._response["result"])

    @property
    def result(self):
        return self._response["result"]

    @property
    def page(self):
        try:
            return self._response["page"]
        except KeyError:
            return None

    def _get_paged_result(self, shift_by):
        if self.page is None:
            raise PaginationError("No pagination available")
        page_number = self.page["page_number"]
        page_to_get = page_number + shift_by
        if page_to_get < 1 or page_to_get > self.page["total_pages"]:
            raise PaginationError("There is no page {}".format(page_to_get))
        args = self._operation_args.copy()
        args.update(
            {"page_size": self.page["page_size"], "page": page_number + shift_by}
        )
        return self._operation(**args)

    def prev_page(self):
        return self._get_paged_result(-1)

    def next_page(self):
        return self._get_paged_result(1)
