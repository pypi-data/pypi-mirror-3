import sys, re

from lxml import html


class HtmlTranslator(object):

    skip_tags = ('script', 'style', html.etree.Comment)
    inline_tags = ('a', 'br', 'span', 'strong', 'em', 'sub', 'sup', 'font', 'b',
                   'i', 'u', 'del', html.etree.Comment)
    #for full list of inline elements see links below:
    #http://htmlhelp.com/reference/html40/inline.html
    #http://www.tutorialchip.com/tutorials/inline-elements-list-whats-new-in-html5/

    process_attribs = ('title', 'alt')
    BREAK_INLINE = object()

    cache_enabled = True
    max_cache_size = 1024*1024*16

    def __init__(self, cache_enabled=cache_enabled, max_cache_size=max_cache_size):
        self.cache_enabled = cache_enabled
        self.max_cache_size = max_cache_size
        self._cache = {}


    def _parse_blocks(self, document):
        text_blocks = []

        inlines = []
        for block in self._parse_text_blocks(document):
            if block == self.BREAK_INLINE:
                    text_blocks.append(tuple(inlines))
                    inlines = []
            else:
                inlines.append(block)
        if inlines:
            text_blocks.append(tuple(inlines))

        attrib_blocks = map(lambda inline: (inline,),
                            self._parse_attrib_blocks(document))

        return text_blocks + attrib_blocks

    def _parse_text_blocks(self, element, root=True):
        if element.tag not in self.skip_tags:

            if element.tag not in self.inline_tags:
                yield self.BREAK_INLINE

            if element.text and element.text.strip():
                yield element.text.strip()

            for child in element:
                for result in self._parse_text_blocks(child, root=False):
                    yield result

        if element.tag not in self.inline_tags:
            yield self.BREAK_INLINE

        #we don't need tail of root element - and it may be not empty if
        #we're translating only part of document
        if (not root) and element.tail and element.tail.strip():
            yield element.tail.strip()

    def _parse_attrib_blocks(self, element):
        for attr in self.process_attribs:
            if element.attrib.has_key(attr) and element.attrib[attr].strip():
                yield element.attrib[attr].strip()

        for child in element:
            for result in self._parse_attrib_blocks(child):
                yield result


    def _replace_blocks(self, document, source_blocks, translation_map):
        #replacing in reverse order - because of list.pop faster implementation
        #also blocks are flat because BREAK_INLINE has no sense anymore

        translated_inlines = []
        for block in source_blocks:
            for inline in translation_map[block]:
                translated_inlines.append(inline)

        self._replace_attrib_blocks(document, translated_inlines)
        self._replace_text_blocks(document, translated_inlines)
        assert not translated_inlines
        return document

    def _replace_text_blocks(self, element, blocks, root=True):
        #we don't need tail of root element - and it may be not empty if
        #we're parsing document part
        if (not root) and element.tail and element.tail.strip():
            element.tail = blocks.pop()

        if element.tag not in self.skip_tags:
            for child in reversed(element):
                self._replace_text_blocks(child, blocks, root=False)

            if element.text and element.text.strip():
                element.text = blocks.pop()

    def _replace_attrib_blocks(self, element, blocks):
        for child in reversed(element):
            self._replace_attrib_blocks(child, blocks)

        for attr in reversed(self.process_attribs):
            if element.attrib.has_key(attr) and element.attrib[attr].strip():
                element.attrib[attr] = blocks.pop()


    #assume there is at least 2 letters successively in a block
    #for some minor issues related matching all unicode letters see:
    #http://stackoverflow.com/questions/2039140/python-re-how-do-i-match-an-alpha-character#2039476
    _translation_needed_regexp = re.compile('[^\W\d_]{2,}', re.UNICODE)

    def translation_needed(self, block):
        return bool(self._translation_needed_regexp.search(u' '.join(block)))


    def parse_language_code(self, document):
        #in case this is part of document
        root = document.getroottree().getroot()
        code = root.attrib.get('lang', '') or root.attrib.get('xml:lang', '')
        return code.split('-')[0].lower() or None

    def translate(self, document, target_language, source_language=None, **kwargs):
        if not isinstance(document, html.HtmlElement):
            if not isinstance(document, basestring):
                raise ValueError('Document must be string or lxml.html.HtmlElement')
            document = html.fromstring(document)

        if not source_language:
            #try to determine language from html
            source_language = self.parse_language_code(document)

        source_blocks = self._parse_blocks(document)
        translation_map = dict.fromkeys(source_blocks)

        if self.cache_enabled:
            if not source_language:
                raise ValueError('Can\'t use cache with language autodetection. '
                                 'Set source_language or cache_enabled=False')
            cache_key = '%s->%s' % (source_language.lower(),
                                    target_language.lower())
            if not cache_key in self._cache:
                self._cache[cache_key] = {}
            cache = self._cache[cache_key]
        else:
            cache = {}

        process_blocks = []
        for block in translation_map:
            if not self.translation_needed(block):
                translation_map[block] = block
            elif block in cache:
                translation_map[block] = cache[block]
            else:
                process_blocks.append(block)

        processed_blocks = self._translate(process_blocks, target_language,
                                           source_language, **kwargs)
        assert len(process_blocks) == len(processed_blocks)

        if self.cache_enabled and self.max_cache_size \
            and (sys.getsizeof(self._cache) + sys.getsizeof(processed_blocks)) \
                > self.max_cache_size:
                self._cache = {cache_key: {}}

        for x in range(len(process_blocks)):
            translation_map[process_blocks[x]] = processed_blocks[x]
            if self.cache_enabled:
                self._cache[cache_key][process_blocks[x]] = processed_blocks[x]
        assert (not None in translation_map.values())

        document = self._replace_blocks(document, source_blocks, translation_map)

        return document

    def _translate(self, blocks, target_language, source_language, **kwargs):
        raise NotImplementedError()
