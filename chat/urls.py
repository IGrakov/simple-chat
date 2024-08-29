from django.urls import path

from chat import views

app_name = 'chat'

urlpatterns = [
    path('create-retrieve-thread/', views.CreateOrRetrieveThreadView.as_view(), name='create_retrieve_thread'),
    path('remove-thread/<int:pk>/', views.DeleteThreadView.as_view(), name='remove_thread'),
    path('retrieve-thread-list/', views.RetrieveListOfThreadsView.as_view(), name='retrieve_thread_list'),
    path('create-retrieve-message/', views.CreateRetrieveMessage.as_view(), name='create_retrieve_message'),
    path(
        'mark-message-as-read/<int:pk>/',
        views.MarkMessageAsReadView.as_view(),
        name='mark_message_as_read'
    ),
    path(
        'retrieve-number-of-unread-messages/',
        views.RetrieveNumberOfUnreadMessages.as_view(),
        name='retrieve_number_of_unread_messages'
    ),
]
