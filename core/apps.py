from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
from django.core.signals import request_started
from .signals import check_vault_token


class CoreConfig(AppConfig):
    name = 'core'
    verbose_name = _('Core')

    def ready(self):
        request_started.connect(check_vault_token)
