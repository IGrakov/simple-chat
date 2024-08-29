from rest_framework.pagination import LimitOffsetPagination

from chat.constants import NUM_OF_ITEMS_PER_PAGE


class ResultsSetPagination(LimitOffsetPagination):
    default_limit = NUM_OF_ITEMS_PER_PAGE
