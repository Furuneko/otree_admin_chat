# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

import base64
import datetime
import io
import logging
import time
import traceback
import urllib.parse

import django.db
import django.utils.timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer, WebsocketConsumer
from django.conf import settings
from django.core.signing import Signer, BadSignature
from django.shortcuts import reverse

import otree.bots.browser
import admin_chat.utils as channel_utils
import otree.session
from admin_chat.utils import get_chat_group
from otree.common import get_models_module
from otree.export import export_wide, export_app
from otree.models import Participant
from .models import (
    AdminChatMessage
)
from otree.models_concrete import ParticipantRoomVisit, BrowserBotsLauncherSessionCode
from otree.room import ROOM_DICT
from otree.session import SESSION_CONFIGS_DICT
from otree.views.admin import CreateSessionForm
import time


logger = logging.getLogger(__name__)

ALWAYS_UNRESTRICTED = 'ALWAYS_UNRESTRICTED'
UNRESTRICTED_IN_DEMO_MODE = 'UNRESTRICTED_IN_DEMO_MODE'


class InvalidWebSocketParams(Exception):
    '''exception to raise when websocket params are invalid'''


class _OTreeAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """
    This is not public API, might change at any time.
    """

    def clean_kwargs(self, **kwargs):
        '''
        subclasses should override if the route receives a comma-separated params arg.
        otherwise, this just passes the route kwargs as is (usually there is just one).
        The output of this method is passed to self.group_name(), self.post_connect,
        and self.pre_disconnect, so within each class, all 3 of those methods must
        accept the same args (or at least take a **kwargs wildcard, if the args aren't used)
        '''
        return kwargs

    def group_name(self, **kwargs):
        raise NotImplementedError()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cleaned_kwargs = self.clean_kwargs(**self.scope['url_route']['kwargs'])
        group_name = self.group_name(**self.cleaned_kwargs)
        self.groups = [group_name] if group_name else []

    unrestricted_when = ''

    # there is no login_required for channels
    # so we need to make our own
    # https://github.com/django/channels/issues/1241
    async def connect(self):

        AUTH_LEVEL = settings.AUTH_LEVEL

        auth_required = (
            (not self.unrestricted_when)
            and AUTH_LEVEL
            or self.unrestricted_when == UNRESTRICTED_IN_DEMO_MODE
            and AUTH_LEVEL == 'STUDY'
        )

        if auth_required and not self.scope['user'].is_staff:
            msg = 'rejected un-authenticated access to websocket path {}'.format(
                self.scope['path']
            )
            # print(msg)
            logger.error(msg)
            # consider also self.accept() then send error message then self.close(code=1008)
            # this only affects otree core websockets.
        else:
            # need to accept no matter what, so we can at least send
            # an error message
            await self.accept()
            await self.post_connect(**self.cleaned_kwargs)

    async def post_connect(self, **kwargs):
        pass

    async def disconnect(self, message, **kwargs):
        await self.pre_disconnect(**self.cleaned_kwargs)

    async def pre_disconnect(self, **kwargs):
        pass

    async def receive_json(self, content, **etc):
        await self.post_receive_json(content, **self.cleaned_kwargs)

    async def post_receive_json(self, content, **kwargs):
        pass


class OTreeAdminChatConsumer(_OTreeAsyncJsonWebsocketConsumer):

    unrestricted_when = ALWAYS_UNRESTRICTED

    def clean_kwargs(self, params):

        signer = Signer(sep='/')
        try:
            original_params = signer.unsign(params)
        except BadSignature:
            raise InvalidWebSocketParams

        channel, participant_id = original_params.split('/')

        return {'channel': channel, 'participant_id': int(participant_id)}

    def group_name(self, channel, participant_id):
        return get_chat_group(channel)

    def _get_history(self, channel):
        return list(
            AdminChatMessage.objects.filter(channel=channel)
                .order_by('timestamp')
                .values('nickname', 'body', 'participant_id', 'timestamp', 'is_seen')
        )

    async def post_connect(self, channel, participant_id):

        history = await database_sync_to_async(self._get_history)(channel=channel)

        # Convert ValuesQuerySet to list
        # but is it ok to send a list (not a dict) as json?
        await self.send_json(history)

    async def post_receive_json(self, content, channel, participant_id):

        # in the Channels docs, the example has a separate msg_consumer
        # channel, so this can be done asynchronously.
        # but i think the perf is probably good enough.
        # moving into here for simplicity, especially for testing.
        if content['message_body']:
            nickname_signed = content['nickname_signed']
            nickname = Signer().unsign(nickname_signed)
            body = content['body']

            chat_message = dict(nickname=nickname, body=body, participant_id=participant_id, timestamp=time.time())

            [group] = self.groups
            await channel_utils.group_send_wrapper(
                type='chat_sendmessages', group=group, event={'chats': [chat_message]}
            )

            await database_sync_to_async(self._create_message)(
                participant_id=participant_id, channel=channel, body=body, nickname=nickname
            )

        else:
            nickname_signed = content['nickname_signed']
            nickname = Signer().unsign(nickname_signed)
            await database_sync_to_async(self._mark_messages_as_seen)(
                participant_id=participant_id, nickname=nickname
            )

    def _create_message(self, **kwargs):
        AdminChatMessage.objects.create(**kwargs)

    def _mark_messages_as_seen(self, participant_id, nickname):
        AdminChatMessage.objects.filter(participant_id=participant_id, is_seen=False)\
            .exclude(nickname=nickname).update(is_seen=True)

    async def chat_sendmessages(self, event):
        chats = event['chats']
        await self.send_json(chats)
