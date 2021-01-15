from django.conf.urls import url
from django.urls import path

from otree.urls import urlpatterns
from admin_chat.pages import (AdminChat)

urlpatterns += [
    url(AdminChat.url_pattern(), AdminChat.as_view(), name=AdminChat.url_name)
]
