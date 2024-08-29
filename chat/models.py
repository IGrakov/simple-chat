from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from core.models import TimeStampMixin
from user.models import User


class Thread(TimeStampMixin):
    participant_one = models.ForeignKey(User, related_name='participant_one_threads', on_delete=models.CASCADE)
    participant_two = models.ForeignKey(User, related_name='participant_two_threads', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            # To avoid case when both participants are the same user, i.e. participant_one=A and participant_two=A
            models.CheckConstraint(
                name='different_participants_in_pair',
                check=~Q(participant_one=F('participant_two')),
                violation_error_message=f'Participant one and Participant two should be different',
            ),
        ]
        verbose_name = 'Thread'

    def save(self, *args, **kwargs):
        # To ensure that Participant one and Participant two make a unique pair
        # participant_one=A and participant_two=B is the same pair as participant_one=B and participant_two=A
        if (Thread.objects.filter(
                participant_one=self.participant_one).filter(participant_two=self.participant_two).exists() or
                Thread.objects.filter(
                    participant_one=self.participant_two).filter(participant_two=self.participant_one).exists()):
            raise ValidationError('The pair of Participant one and Participant two already exists')
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f'Thread No.{self.id} for {self.participant_one.email} and {self.participant_two.email}'


class Message(TimeStampMixin):
    sender = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    thread = models.ForeignKey(Thread, related_name='messages', on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Message'

    def __str__(self):
        return f'Message for thread No.{self.thread} by {self.sender.email}'
