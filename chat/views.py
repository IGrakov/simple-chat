from django.db import IntegrityError
from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import generics, status, serializers
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    inline_serializer,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Message, Thread
from chat.pagination import ResultsSetPagination
from chat.serializers import MessageSerializer, ThreadReadSerializer, SwaggerCreateMessageSerializer, \
    ThreadWriteSerializer
from user.serializers import UserSerializer


@extend_schema_view(
    post=extend_schema(
        responses={
            status.HTTP_200_OK: ThreadReadSerializer(),
            status.HTTP_201_CREATED: ThreadReadSerializer(),
        },
    )
)
class CreateOrRetrieveThreadView(generics.RetrieveAPIView, generics.CreateAPIView):
    """Create thread for particular users. If a thread with such users already exists, return the thread"""
    serializer_class = ThreadWriteSerializer
    queryset = Thread.objects.all()
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except (IntegrityError, ValidationError) as e:
            if e.args[0] == 'The pair of Participant one and Participant two already exists':
                participant_one = serializer.validated_data['participant_one']
                participant_two = serializer.validated_data['participant_two']
                thread = Thread.objects.filter(participant_one=participant_one,
                                               participant_two=participant_two).first() or Thread.objects.filter(
                    participant_one=participant_two, participant_two=participant_one).first()
                return Response(ThreadReadSerializer(thread).data, status=status.HTTP_200_OK)
            return Response({'message': e.args[0]}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class DeleteThreadView(generics.DestroyAPIView):
    """Delete thread by id"""
    serializer_class = ThreadReadSerializer
    queryset = Thread.objects.all()


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name='user',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.INT
            ),
        ],
    )
)
class RetrieveListOfThreadsView(generics.ListAPIView):
    """Retrieve list of threads for any user"""
    serializer_class = ThreadReadSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        user = self.request.query_params.get('user')
        return Thread.objects.filter(
            Q(participant_one=user) | Q(participant_two=user)).select_related(
            'participant_one', 'participant_two')


@extend_schema_view(
    get=extend_schema(
        description='Retrieve message list for particular thread',
        parameters=[
            OpenApiParameter(
                name='thread_id',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.INT
            ),
        ],
    ),
    post=extend_schema(
        description='Create message for particular thread',
        request=SwaggerCreateMessageSerializer,
        parameters=[
            OpenApiParameter(
                name='text',
                location=OpenApiParameter.QUERY,
                required=False,
                type=OpenApiTypes.STR
            ),
            OpenApiParameter(
                name='thread',
                location=OpenApiParameter.QUERY,
                required=True,
                type=OpenApiTypes.INT
            ),
        ],
    )
)
class CreateRetrieveMessage(generics.CreateAPIView, generics.ListAPIView):
    """Create message and retrieve message list for particular thread"""
    serializer_class = MessageSerializer
    pagination_class = ResultsSetPagination

    def get_queryset(self):
        thread_id = self.request.query_params.get('thread_id')
        return Message.objects.filter(thread=thread_id).select_related('sender')

    def perform_create(self, serializer):
        serializer.save(
            sender=self.request.user
        )


@extend_schema_view(
    patch=extend_schema(
        request=inline_serializer(
            name='EmptyInlineSerializer',
            fields={},
        )
    )
)
class MarkMessageAsReadView(generics.UpdateAPIView):
    """Mark particular message as read"""
    serializer_class = MessageSerializer
    queryset = Message.objects.all()
    http_method_names = ["patch"]

    def perform_update(self, serializer):
        serializer.save(
            is_read=True,
        )


@extend_schema_view(
    get=extend_schema(
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='NumberOfUnreadMessagesSerializer',
                fields={
                    'user': UserSerializer(),
                    'number_of_unread_messages': serializers.IntegerField(),
                }
            ),
        },
    )
)
class RetrieveNumberOfUnreadMessages(APIView):
    """Retrieve number of unread messages for authenticated user"""

    def get(self, request, *args, **kwargs):
        user = UserSerializer(self.request.user).data
        return Response({
            'user': user,
            'number_of_unread_messages': Message.objects.filter(sender=self.request.user, is_read=False).count()
        })
