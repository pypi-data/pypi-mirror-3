from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import DebugPanel


class PrintTemplateNamePanel(DebugPanel):
    has_content = True
    name = 'Print Template Name Panel'
    template = 'debug_toolbar_extra/panels/print_template_name_panel.html'

    def __init__(self, *args, **kwargs):
        super(PrintTemplateNamePanel, self).__init__(*args, **kwargs)
        print_template_name()

    def url(self):
        return ''

    def nav_title(self):
        return _('Print template name')

    def title(self):
        return self.nav_title()


def print_template_name(start_token='Start', end_token='End'):
    if not settings.DEBUG or not settings.TEMPLATE_DEBUG:
        return
    from django.template import Template

    def printed_template_name_test_render(self, context):
        content = self.instrumented_test_render(context)
        without_template = '/with/out/indetify/template.html'
        template = getattr(self, 'origin', without_template) and getattr(self.origin, 'name', without_template) or without_template
        return mark_safe(u"<!-- %s %s -->\n %s \n<!-- %s %s -->" % (start_token,
                                                                template,
                                                                content,
                                                                end_token,
                                                                template))
    if not getattr(Template, 'instrumented_test_render', None) or Template._render.im_func.func_name != 'printed_template_name_test_render':
        # https://code.djangoproject.com/browser/django/trunk/django/test/utils.py#L72
        Template.instrumented_test_render = Template._render
        Template._render = printed_template_name_test_render
