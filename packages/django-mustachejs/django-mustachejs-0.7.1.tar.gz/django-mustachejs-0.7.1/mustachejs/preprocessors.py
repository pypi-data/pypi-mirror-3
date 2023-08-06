import re
from django.utils.translation import ugettext
from .conf import conf

class I18nPreprocessor(object):
    @property
    def tagnames(self):
        return conf.MUSTACHEJS_I18N_TAGS

    @property
    def trans_re(self):
        # Should match strings like: {{# _ }}Hello, {{ name }}.{{/ _ }}
        tagnames = '|'.join(['(?:{0})'.format(t) for t in self.tagnames])
        start_tag = r'\{\{#\s*(?:' + tagnames + r')\s*\}\}'
        end_tag = r'\{\{\/\s*(?:' + tagnames + r')\s*\}\}'

        return start_tag + '(.*)' + end_tag

    def translate(self, match):
        """Translate a result of matching the compiled trans_re pattern."""
        string = match.group(1)
        return ugettext(string) if len(string) > 0 else u''

    def process(self, content):
        return re.sub(self.trans_re, self.translate, content, flags=re.DOTALL)
