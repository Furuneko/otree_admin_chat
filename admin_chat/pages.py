from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import View, FormView, TemplateView
from django.urls import reverse_lazy

from django.core.signing import Signer
from . import utils as channel_utils
from django.utils.translation import ugettext as _

import vanilla
from django.urls import reverse
from otree.views.abstract import AdminSessionPageMixin


class UNDEFINED:
    pass


class AdminChat(AdminSessionPageMixin, vanilla.TemplateView):
    url_name = 'AdminChat'

    def get_template_names(self):
        return ['admin/{}.html'.format(self.__class__.__name__)]

    def vars_for_template(self, nickname=UNDEFINED):
        session = self.session
        room = session.get_room()
        participants = session.get_participants()

        prefixed_channel = '{}'.format(session.code)

        if nickname == UNDEFINED:
            nickname = _('Experimenter')
        nickname = str(nickname)
        nickname_signed = Signer().sign(nickname)

        sockets_paths = [channel_utils.chat_path(prefixed_channel+'-{}'.format(p.id), p.id) for p in participants]

        context = dict(
            participants=participants,
            channel=prefixed_channel,
            sockets_paths=sockets_paths,
            nickname_signed=nickname_signed,
            nickname=nickname,
            nickname_i_see_for_myself=_("{nickname} (Me)").format(nickname=nickname)
        )

        if room:
            context.update(
                room=room,
            )

        return context
