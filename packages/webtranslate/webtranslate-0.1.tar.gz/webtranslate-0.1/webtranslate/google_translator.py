from lxml import html

from webtranslate.translator import HtmlTranslator
import google_translate


class GoogleHtmlTranslator(HtmlTranslator):
    def _zip_inlines(self, inlines):
        if len(inlines) == 1:
            return inlines[0]
        #make it looks just like in official clients
        return u''.join([u'<a i=%d>%s</a>' % (i, inline) for i, inline
                         in enumerate(inlines)])

    def _unzip_inlines(self, string):
        if string.startswith('<a'):
            return map(lambda e: e.text, html.fromstring(string))
        else:
            return (string,)

    def _translate(self, blocks, target_language, source_language, **kwargs):
        blocks = map(self._zip_inlines, blocks)
        result = google_translate.translate(blocks, target_language, source_language, **kwargs)
        return map(self._unzip_inlines, result[0])
