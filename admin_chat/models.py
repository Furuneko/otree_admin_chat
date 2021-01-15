from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import time
from django.db import models
from otree.models import Session


author = 'Your name here'

doc = """
Your app description
"""

def get_channel_name(session: Session) -> str:
    return f'session_{session.code}'


class Constants(BaseConstants):
    name_in_url = 'admin_chat'
    players_per_group = None
    num_rounds = 1

    instructions_template = 'admin_chat/instructions.html'
    # """Amount allocated to each player"""
    endowment = c(100)
    multiplier = 2


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


class AdminChatMessage(models.Model):
    class Meta:
        index_together = ['channel', 'timestamp']

    # the name "channel" here is unrelated to Django channels
    channel = models.CharField(max_length=255)
    # related_name necessary to disambiguate with otreechat add on
    participant = models.ForeignKey(
        'otree.Participant', related_name='admin_chat_messages', on_delete=models.CASCADE
    )
    nickname = models.CharField(max_length=255)

    # call it 'body' instead of 'message' or 'content' because those terms
    # are already used by channels
    body = models.TextField()
    timestamp = models.FloatField(default=time.time)

    is_seen = models.BooleanField(default=False)

