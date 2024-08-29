from rest_framework.pagination import LimitOffsetPagination


class ResultsSetPagination(LimitOffsetPagination):
    default_limit = 10
