from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    """Pagination class that paginates responses into distinct page numbers.

    Extends PageNumberPagination- which handles the actual pagination logic.

    Attributes:
        page_size (int): The number of objects on each page.
        page_size_query_param (String): The query string that is used to choose the page size.
        max_page_size (int): The maximum number of objects per page.
    """

    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100