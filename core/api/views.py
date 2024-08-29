from django.http.request import HttpRequest
from django.http.response import HttpResponse


def health(request: HttpRequest) -> HttpResponse:
    return HttpResponse(status=200)
