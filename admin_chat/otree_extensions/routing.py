from django.conf.urls import url
from admin_chat.consumers import OTreeAdminChatConsumer

websocket_routes = [
    url(r"^otree_admin_chat/(?P<params>[a-zA-Z0-9_/-]+)/$", OTreeAdminChatConsumer),
]
