import re
from django.template.backends.django import DjangoTemplates
from django.template import base as template_base


class MultiLineTemplateEngine(DjangoTemplates):
    """
    Custom template engine that allows multiline tags.
    """

    def __init__(self, params):
        super().__init__(params)
        template_base.tag_re = re.compile(template_base.tag_re.pattern, re.DOTALL)
