from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from chat.constants import NUM_OF_ITEMS_PER_PAGE
from chat.factories import ThreadFactory, MessageFactory
from chat.models import Thread, Message
from user.factories import UserFactory

CREATE_RETRIEVE_THREAD_URL = reverse('chat:create_retrieve_thread')
RETRIEVE_THREAD_LIST_URL = reverse('chat:retrieve_thread_list')
CREATE_RETRIEVE_MESSAGE_URL = reverse('chat:create_retrieve_message')
RETRIEVE_NUMBER_OF_UNREAD_MESSAGES = reverse('chat:retrieve_number_of_unread_messages')


class PublicChatApiTests(TestCase):
    """Test chat API (public)"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()

    def test_create_retrieve_thread_fail(self):
        """Test creating or retrieving a thread with an unauthenticated user"""
        participant_two = UserFactory.create()
        payload = {
            'participant_one': self.user.id,
            'participant_two': participant_two.id,
        }
        res = self.client.post(CREATE_RETRIEVE_THREAD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_remove_thread_fail(self):
        """Test removing a thread with an unauthenticated user"""
        ThreadFactory.create()
        thread_id = Thread.objects.first().id
        res = self.client.delete(reverse('chat:remove_thread', kwargs={'pk': thread_id}))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_thread_list_fail(self):
        """Test retrieving threads list with an unauthenticated user"""
        ThreadFactory.create_batch(2)
        res = self.client.get(RETRIEVE_THREAD_LIST_URL, {'user': self.user.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_message_fail(self):
        """Test creating a message with an unauthenticated user"""
        thread = ThreadFactory.create()
        payload = {
            'text': 'Test message',
            'thread': thread.id,
        }
        res = self.client.post(CREATE_RETRIEVE_MESSAGE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_message_list_fail(self):
        """Test retrieving message list for a particular thread with an unauthenticated user"""
        thread = ThreadFactory.create()
        MessageFactory.create_batch(2, thread=thread)
        res = self.client.get(CREATE_RETRIEVE_MESSAGE_URL, {'thread_id': thread.id})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_message_as_read_fail(self):
        """Test marking message as read with an unauthenticated user"""
        thread = ThreadFactory.create(participant_one=self.user)
        message = MessageFactory(thread=thread)
        res = self.client.patch(reverse('chat:mark_message_as_read', kwargs={'pk': message.id}))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_number_of_unread_messages_fail(self):
        """Test retrieving number of unread messages with an unauthenticated user"""
        thread = ThreadFactory()
        MessageFactory.create_batch(2, thread=thread, sender=self.user)
        res = self.client.get(RETRIEVE_NUMBER_OF_UNREAD_MESSAGES)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateChatApiTests(TestCase):
    """Test chat API (private)"""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_thread_success(self):
        """Test creating a thread with an authenticated user"""
        participant_two = UserFactory.create()
        payload = {
            'participant_one': self.user.id,
            'participant_two': participant_two.id,
        }
        res = self.client.post(CREATE_RETRIEVE_THREAD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        thread = Thread.objects.first()
        self.assertEqual(thread.participant_one.id, self.user.id)
        self.assertEqual(thread.participant_two.id, participant_two.id)

    def test_retrieve_thread_success(self):
        """Test retrieving already existing thread when trying to create it
        with the same unique pair of members with an authenticated user"""
        participant_one = UserFactory.create()
        participant_two = UserFactory.create()
        ThreadFactory(participant_one=participant_one, participant_two=participant_two)
        payload = {
            'participant_one': participant_one.id,
            'participant_two': participant_two.id,
        }
        res = self.client.post(CREATE_RETRIEVE_THREAD_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(Thread.objects.count(), 1)
        self.assertEqual(res.json().get('participant_one').get('id'), participant_one.id)
        self.assertEqual(res.json().get('participant_two').get('id'), participant_two.id)

    def test_remove_thread_success(self):
        """Test removing a thread with an authenticated user"""
        ThreadFactory.create()
        thread_id = Thread.objects.first().id
        res = self.client.delete(reverse('chat:remove_thread', kwargs={'pk': thread_id}))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Thread.objects.first(), None)

    def test_retrieve_thread_list_success(self):
        """Test retrieving thread list with an authenticated user"""
        user1 = UserFactory()
        user2 = UserFactory()
        ThreadFactory.create(participant_one=user1)
        ThreadFactory.create(participant_two=user1)
        ThreadFactory.create(participant_one=user2)
        res = self.client.get(RETRIEVE_THREAD_LIST_URL, {'user': user1.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()['results']), 2)

    def test_retrieve_paginated_thread_list_success(self):
        """Test retrieving paginated thread list with an authenticated user"""
        user = UserFactory()
        ThreadFactory.create_batch(NUM_OF_ITEMS_PER_PAGE + 1, participant_one=user)
        res = self.client.get(RETRIEVE_THREAD_LIST_URL, {'user': user.id, 'offset': NUM_OF_ITEMS_PER_PAGE})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()['results']), 1)

    def test_create_message_success(self):
        """Test creating a message with an authenticated user"""
        thread = ThreadFactory.create()
        payload = {
            'text': 'Test message',
            'thread': thread.id,
        }
        res = self.client.post(CREATE_RETRIEVE_MESSAGE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        message = Message.objects.first()
        result = {
            'text': message.text,
            'thread': message.thread.id,
        }
        self.assertEqual(result, payload)
        self.assertEqual(message.sender.id, self.user.id)

    def test_retrieve_message_list_success(self):
        """Test retrieving message list for a particular thread with an authenticated user"""
        thread = ThreadFactory.create()
        MessageFactory.create_batch(2, thread=thread)
        res = self.client.get(CREATE_RETRIEVE_MESSAGE_URL, {'thread_id': thread.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()['results']), 2)

    def test_retrieve_paginated_message_list_success(self):
        """Test retrieving paginated message list for a particular thread with an authenticated user"""
        thread = ThreadFactory.create()
        MessageFactory.create_batch(NUM_OF_ITEMS_PER_PAGE + 1, thread=thread)
        res = self.client.get(CREATE_RETRIEVE_MESSAGE_URL, {'thread_id': thread.id, 'offset': NUM_OF_ITEMS_PER_PAGE})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.json()['results']), 1)

    def test_mark_message_as_read_success(self):
        """Test marking message as read with an authenticated user"""
        thread = ThreadFactory.create(participant_one=self.user)
        message = MessageFactory(thread=thread)
        self.assertEqual(message.is_read, False)
        res = self.client.patch(reverse('chat:mark_message_as_read', kwargs={'pk': message.id}))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        saved_message = Message.objects.first()
        self.assertEqual(saved_message.is_read, True)

    def test_retrieve_number_of_unread_messages_success(self):
        """Test retrieving number of unread messages with an authenticated user"""
        thread = ThreadFactory()
        MessageFactory.create_batch(2, thread=thread, sender=self.user)
        MessageFactory.create_batch(2, thread=thread, sender=self.user, is_read=True)
        res = self.client.get(RETRIEVE_NUMBER_OF_UNREAD_MESSAGES)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json().get('number_of_unread_messages'), 2)
