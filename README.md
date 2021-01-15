# oTree Admin Chat

Add-on that allows an experimenter to chat in real time with the participants of an oTree session.

### How to use it

The admin chat can be added in three steps:
* Include the folders _template/otree and admin_chat in the root folder of your oTree project.
* Update your settings.py by including the admin_chat app in the lists of your INSTALLED_APPS and EXTENSION_APPS
and by setting ROOT_URLCONF = 'admin_chat.urls'(see example in this repository):

    ```python
    INSTALLED_APPS = ['otree', 'admin_chat']
    EXTENSION_APPS = ['admin_chat']
    ROOT_URLCONF = 'admin_chat.urls'
    ```
* In your template html file, load the otree_admin_chat and use it with the tag {% admin_chat %} 
(see example in this repository):

    ```python
    {% load otree static otree_admin_chat %}

    {% block content %}
        <!-- Admin chat tag here -->
        {% admin_chat %}
    {% endblock %}
    ```

### Preview

A preview is available [here](https://cess-nuffield.nuff.ox.ac.uk/virtual-lab).

### Live example

A live example is available [here](https://otree-admin-chat.herokuapp.com "oTree Admin Chat").

### Compatibility

This add-on has been tested with otree >= 3.2.3 
