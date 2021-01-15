from django import template
from admin_chat.admin_chat import admin_chat_template_tag


register = template.Library()


@register.inclusion_tag('otree_admin_chat/widget.html', takes_context=True, name='admin_chat')
def admin_chat(context, *args, **kwargs):
    return admin_chat_template_tag(context, *args, **kwargs)
