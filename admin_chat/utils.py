from django.core.signing import Signer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from urllib.parse import urlencode

_group_send = get_channel_layer().group_send
_sync_group_send = async_to_sync(_group_send)


def sync_group_send_wrapper(*, type: str, group: str, event: dict):
    '''make it a function that takes proper args that are intuitive.
    enforces correct use.
    '''
    return _sync_group_send(group, {'type': type, **event})


def group_send_wrapper(*, type: str, group: str, event: dict):
    '''make it a function that takes proper args that are intuitive.
    '''
    return _group_send(group, {'type': type, **event})


def chat_path(channel, participant_id):
    channel_and_id = '{}/{}'.format(channel, participant_id)
    channel_and_id_signed = Signer(sep='/').sign(channel_and_id)

    return '/otree_admin_chat/{}/'.format(channel_and_id_signed)


def get_chat_group(channel):
    return 'otree_admin_chat-{}'.format(channel)

