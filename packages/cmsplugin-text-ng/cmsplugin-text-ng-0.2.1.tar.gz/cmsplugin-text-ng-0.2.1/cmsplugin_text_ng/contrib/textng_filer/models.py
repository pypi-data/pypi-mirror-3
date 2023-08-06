# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from tinymce.models import HTMLField

from cmsplugin_text_ng.models import TextNGVariableBase
from cmsplugin_text_ng.type_registry import register_type

class TextNGVariableHTML(TextNGVariableBase):
    value = HTMLField(null=True, blank=True, verbose_name=_('value'))

    class Meta:
        verbose_name = _('html text')
        verbose_name_plural = _('html texts')

register_type('htmltext', TextNGVariableHTML)

