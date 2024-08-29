import factory
import faker

from chat.models import Message, Thread
from user.factories import UserFactory


class ThreadFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Thread

    participant_one = factory.SubFactory(UserFactory)
    participant_two = factory.SubFactory(UserFactory)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Message

    sender = factory.SubFactory(UserFactory)
    text = factory.Faker('sentence')
    thread = factory.SubFactory(ThreadFactory)
