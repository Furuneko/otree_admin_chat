import re
from django.core.signing import Signer
from . import utils as channel_utils
from django.utils.translation import ugettext as _


class ChatTagError(Exception):
    pass


class UNDEFINED:
    pass


def admin_chat_template_tag(context, *, channel=UNDEFINED, nickname=UNDEFINED):
    player = context['player']
    group = context['group']
    Constants = context['Constants']
    participant = context['participant']

    # TB: set fixed channel base
    # if channel == UNDEFINED:
    #     channel = group.id
    # channel = str(channel)
    # channel name should not contain illegal chars,
    # so that it can be used in JS and URLs
    # if not re.match(r'^[a-zA-Z0-9_-]+$', channel):
    #     msg = (
    #         "'channel' can only contain ASCII letters, numbers, underscores, and hyphens. "
    #         "Value given was: {}".format(channel)
    #     )
    #     raise ChatTagError(msg)
    # prefix the channel name with session code and app name
    prefixed_channel = '{}-{}'.format(
        # TB: from session.id to session.code
        context['session'].code,
        participant.id
        # TB: removed app url and var channel from prefixed channel

        # previously used a hash() here to ensure name_in_url is the same,
        # but hash() is non-reproducible across processes
        # channel,
    )
    context['channel'] = prefixed_channel

    if nickname == UNDEFINED:
        # Translators: A player's default chat nickname,
        # which is "Player" + their ID in group. For example:
        # "Player 2".

        # TB: from player.id_in_group to participant.id_in_session
        nickname = _('Participant {id_in_session}').format(id_in_session=participant.id_in_session)
    nickname = str(nickname)
    nickname_signed = Signer().sign(nickname)

    socket_path = channel_utils.chat_path(prefixed_channel, participant.id)

    chat_vars_for_js = {
        'socket_path': socket_path,
        'channel': prefixed_channel,
        'participant_id': participant.id,
        'nickname_signed': nickname_signed,
        'nickname': nickname,
        # Translators: the name someone sees displayed for themselves in a chat.
        # It's their nickname followed by "(Me)". For example:
        # "Michael (Me)" or "Player 1 (Me)".
        'nickname_i_see_for_myself': _("{nickname} (Me)").format(nickname=nickname),
    }

    context['chat_vars_for_js'] = chat_vars_for_js

    return context
