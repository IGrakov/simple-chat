from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.authtoken.models import Token
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)

from .models import User
from .pagination import ResultsSetPagination
from .serializers import (
    UserSerializer,
    AuthTokenSerializer
)


@extend_schema_view(
    post=extend_schema(
        parameters=[
            OpenApiParameter(
                name='email',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.EMAIL
            ),
            OpenApiParameter(
                name='password',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='first_name',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='last_name',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
        ],
    )
)
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = (AllowAny, )


@extend_schema_view(
    post=extend_schema(
        parameters=[
            OpenApiParameter(
                name='email',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.EMAIL
            ),
            OpenApiParameter(
                name='password',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
        ],
    )
)
class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user"""
    serializer_class = AuthTokenSerializer
    permission_classes = (AllowAny, )
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'user_id': user.id})


@extend_schema_view(
    get=extend_schema(
        description='Retrieve authenticated user',
    ),
    put=extend_schema(
        description='Update authenticated user',
        parameters=[
            OpenApiParameter(
                name='email',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.EMAIL
            ),
            OpenApiParameter(
                name='password',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='first_name',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='last_name',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.STR
            ),
        ],
    ),
    patch=extend_schema(
        description='Partially update authenticated user',
        parameters=[
            OpenApiParameter(
                name='email',
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.EMAIL
            ),
            OpenApiParameter(
                name='password',
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='first_name',
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='last_name',
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR
            ),
        ],
    )
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage authenticated user"""
    serializer_class = UserSerializer

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ListUserView(generics.ListAPIView):
    """Retrieve list of users in the system"""
    serializer_class = UserSerializer
    queryset = User.objects.all()
    pagination_class = ResultsSetPagination
