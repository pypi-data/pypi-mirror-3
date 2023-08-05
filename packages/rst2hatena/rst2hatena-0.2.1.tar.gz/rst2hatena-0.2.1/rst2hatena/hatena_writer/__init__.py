#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Hatena document writer
"""
from docutils import writers, nodes

from base_translator import BaseTranslator


class Writer(writers.UnfilteredWriter):

    supported = ('hatena',)
    """Formats this writer supports."""

    config_section = 'hatena writer'
    config_section_dependencies = ('writers',)

    def translate(self):
        visitor = HatenaTranslator(self.document)
        self.document.walkabout(visitor)
#        print self.document.pformat()
        self.output = visitor.astext()


class HatenaTranslator(BaseTranslator):
    """
    """
    def __init__(self, document):
        BaseTranslator.__init__(self, document)

        self.section_level = 0
        self.initial_header_level = 1  # TODO: int(settings.initial_header_level)
        self.line_block_level = 0
        self.list_level = 0
        self.is_enum = True
        self.block_quote_level = 0

        self.in_reference = None
        self.in_internal_reference = None
        self.in_line = None
        self.in_definition = None
        self.in_paragraph = None
        self.in_thead = None
        self.in_comment = None
        self.in_author = None

        self.footnote_idx_dict = {}
        self.footnote_idx = 0
        self.footnote_ids = None

        self.in_citation_key = None
        self.citation_idx_dict = {}
        self.citation_idx = 0
        self.citation_ids = None

    def astext(self):
        return ''.join(self.body)

    def visit_Text(self, node):
        text = node.astext()
        if self.in_definition or self.in_line or self.in_comment \
                or self.in_paragraph or self.in_author:
            text = ' '.join(text.split('\n'))
        self.body.append(text)

    def depart_Text(self, node):
        pass

    # ================
    #  Title Elements
    # ================

    def visit_title(self, node):
        if isinstance(node.parent, nodes.topic):
            self.body.append(':')
        elif isinstance(node.parent, nodes.document):
            self.body.append('*' * self.initial_header_level)
        else:
            h_level = self.section_level + self.initial_header_level
            if h_level > 3:
                h_level = 3
            self.body.append('*' * h_level)

    def depart_title(self, node):
        if isinstance(node.parent, nodes.topic):
            self.body.append(':')
            return
        self.body.append('\n')
        self.body.append('\n')

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.body.append('*' * (self.initial_header_level + 1))
        elif isinstance(node.parent, nodes.section):
            h_level = self.section_level + self.initial_header_level
            if h_level > 3:
                h_level = 3
            self.body.append('*' * h_level)

    def depart_subtitle(self, node):
        self.body.append('\n')
        self.body.append('\n')

    # ========================
    #  Bibliographic Elements
    # ========================
    def visit_author(self, node):
        self.in_author = 1
        self.body.append(':Author:')

    def depart_author(self, node):
        self.in_author = None
        self.body.append('\n')

    def visit_organization(self, node):
        self.body.append(':Organization:')

    def depart_organization(self, node):
        self.body.append('\n')

    def visit_address(self, node):
        self.body.append(':Address:')

    def depart_address(self, node):
        self.body.append('\n')

    def visit_contact(self, node):
        self.body.append(':Contact:')

    def depart_contact(self, node):
        self.body.append('\n')

    def visit_version(self, node):
        self.body.append(':Version:')

    def depart_version(self, node):
        self.body.append('\n')

    def visit_revision(self, node):
        self.body.append(':Revision:')

    def depart_revision(self, node):
        self.body.append('\n')

    def visit_status(self, node):
        self.body.append(':Status:')

    def depart_status(self, node):
        self.body.append('\n')

    def visit_date(self, node):
        self.body.append(':Date:')

    def depart_date(self, node):
        self.body.append('\n')

    def visit_copyright(self, node):
        self.body.append(':Copyright:')

    def depart_copyright(self, node):
        self.body.append('\n')

    # =====================
    #  Structural Elements
    # =====================

    def visit_section(self, node):
        self.section_level += 1

    def depart_section(self, node):
        self.section_level -= 1

    def visit_topic(self, node):
        self.in_definition = 1

    def depart_topic(self, node):
        self.in_definition = None

    def visit_transition(self, node):
        self.body.append('<hr>')

    def depart_transition(self, node):
        self.body.append('\n')
        self.body.append('\n')

    # ===============
    #  Body Elements
    # ===============

    def visit_paragraph(self, node):
        self.in_paragraph = 1

    def depart_paragraph(self, node):
        self.in_paragraph = None
        if isinstance(node.parent, nodes.entry) or self.footnote_idx != 0 or self.citation_idx != 0:
            return
        self.body.append('\n')
        if not isinstance(node.parent, nodes.list_item) \
                and not isinstance(node.parent, nodes.system_message) \
                and not isinstance(node.parent, nodes.topic) \
                and not isinstance(node.parent, nodes.block_quote) and self.block_quote_level != 1:
            self.body.append('\n')

    def visit_bullet_list(self, node):
        self.is_enum = False
        self.list_level += 1

    def depart_bullet_list(self, node):
        self.list_level -= 1
        if not isinstance(node.parent, nodes.list_item) \
                and not isinstance(node.parent, nodes.entry):
            self.body.append('\n')

    def visit_enumerated_list(self, node):
        self.is_enum = True
        self.list_level += 1

    def depart_enumerated_list(self, node):
        self.list_level -= 1
        if not isinstance(node.parent, nodes.list_item) \
                and not isinstance(node.parent, nodes.entry):
            self.body.append('\n')

    def visit_list_item(self, node):
        if self.is_enum:
            li = '+'
        else:
            li = '-'
        self.body.append(li * (self.list_level))
        self.body.append(' ')

    def depart_list_item(self, node):
        pass

    def visit_term(self, node):
        self.body.append(':')

    def depart_term(self, node):
        self.body.append(':')

    def visit_definition(self, node):
        self.in_definition = 1

    def depart_definition(self, node):
        self.in_definition = None
        pass

    def visit_field_name(self, node):
        self.body.append(':')

    def depart_field_name(self, node):
        self.body.append(':')

    def visit_option(self, node):
        self.body.append(':')

    def depart_option(self, node):
        self.body.append(':')

    def visit_option_argument(self, node):
        if node.has_key('delimiter'):
            self.body.append(node['delimiter'])

    def depart_option_argument(self, node):
        pass

    def visit_option_list_item(self, node):
        self.in_definition = 1

    def depart_option_list_item(self, node):
        self.in_definition = None

    def visit_literal_block(self, node):
        self.body.append('>||')
        self.body.append('\n')

    def depart_literal_block(self, node):
        self.body.append('\n')
        self.body.append('||<')
        self.body.append('\n')
        self.body.append('\n')

    def visit_line_block(self, node):
        if self.line_block_level == 0:
            self.body.append('>|')
            self.body.append('\n')
        self.line_block_level += 1

    def depart_line_block(self, node):
        self.line_block_level -= 1
        if self.line_block_level == 0:
            self.body.append('|<')
            self.body.append('\n')
            self.body.append('\n')

    def visit_line(self, node):
        self.in_line = 1
        self.body.append('    ' * (self.line_block_level - 1))

    def depart_line(self, node):
        self.in_line = None
        self.body.append('\n')

    def visit_doctest_block(self, node):
        self.body.append('>|python|')
        self.body.append('\n')

    def depart_doctest_block(self, node):
        self.body.append('\n')
        self.body.append('||<')
        self.body.append('\n')
        self.body.append('\n')

    def visit_block_quote(self, node):
        self.block_quote_level += 1
        if self.block_quote_level == 1:
            self.body.append('>>')
        self.body.append('\n')
        self.body.append('    ' * (self.block_quote_level - 1))

    def depart_block_quote(self, node):
        self.block_quote_level -= 1
        if self.block_quote_level == 0:
            self.body.append('<<')
            self.body.append('\n')
            self.body.append('\n')

    def visit_comment(self, node):
        self.in_comment = 1
        self.body.append('<!--\n')

    def depart_comment(self, node):
        self.in_comment = None
        self.body.append('\n')
        self.body.append('-->\n')
        self.body.append('\n')

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def depart_substitution_definition(self, node):
        pass

    def visit_target(self, node):
        if node.has_key('refid'):
            self.body.append('<a name="%s"></a>' % node['refid'])
            self.body.append('\n')

    def depart_target(self, node):
        pass

    def visit_thead(self, node):
        self.in_thead = 1

    def depart_thead(self, node):
        self.in_thead = None

    def visit_tbody(self, node):
        pass

    def depart_tbody(self, node):
        self.body.append('\n')

    def visit_row(self, node):
        pass

    def depart_row(self, node):
        self.body.append('|')
        self.body.append('\n')

    def visit_entry(self, node):
        self.body.append('|')
        if self.in_thead:
            self.body.append('*')

    def depart_entry(self, node):
        pass

    def visit_footnote(self, node):
        if not node.has_key('ids'):
            raise nodes.SkipNode
        self.footnote_ids = node['ids'][0]
        if not self.footnote_idx_dict.has_key(self.footnote_ids):
            raise nodes.SkipNode
        self.footnote_idx = len(self.body)

    def depart_footnote(self, node):
        footnote = self.body[self.footnote_idx:]
        for idx in self.footnote_idx_dict[self.footnote_ids]:
            self.body[idx] = ''.join(footnote)
        del self.body[self.footnote_idx:]
        self.footnote_idx = 0

    def visit_citation(self, node):
        if not node.has_key('ids'):
            raise nodes.SkipNode
        self.citation_ids = node['ids'][0]
        if not self.citation_idx_dict.has_key(self.citation_ids):
            raise nodes.SkipNode
        self.citation_idx = len(self.body)

    def depart_citation(self, node):
        citation = self.body[self.citation_idx:]
        for idx in self.citation_idx_dict[self.citation_ids]:
            self.body[idx] = ''.join(citation)
        del self.body[self.citation_idx:]
        self.citation_idx = 0

    def visit_label(self, node):
        raise nodes.SkipNode

    def visit_system_message(self, node):
        self.body.append('<!--\n')

    def depart_system_message(self, node):
        self.body.append('-->\n')
        self.body.append('\n')

    # =================
    #  Inline Elements
    # =================

    def visit_emphasis(self, node):
        self.body.append('<span style="font-style:italic;">')

    def depart_emphasis(self, node):
        self.body.append('</span>')

    def visit_strong(self, node):
        self.body.append('<span style="font-weight:bold;">')

    def depart_strong(self, node):
        self.body.append('</span>')

    def visit_literal(self, node):
        self.body.append('<span style="font-style:italic;">')

    def depart_literal(self, node):
        self.body.append('</span>')

    def visit_reference(self, node):
        if node.has_key('refuri'):
            self.in_reference = 1
            href = node['refuri']
            self.body.append('[')
            self.body.append(href)
            self.body.append(':title=')
        elif node.has_key('refid'):
            self.in_internal_reference = 1
            self.body.append('<a href="#%s">' % node['refid'])

    def depart_reference(self, node):
        if self.in_reference:
            self.body.append(']')
        if self.in_internal_reference:
            self.body.append('</a>')
        if not isinstance(node.parent, nodes.TextElement):
            self.body.append('\n')
        self.in_reference = None
        self.in_internal_reference = None

    def visit_title_reference(self, node):
        self.body.append('<span style="font-style:italic;">')

    def depart_title_reference(self, node):
        self.body.append('</span>')

    def visit_footnote_reference(self, node):
        if not node.has_key('refid'):
            raise nodes.SkipNode
        key = node['refid']
        self.body.append('((')
        if not self.footnote_idx_dict.has_key(key):
            self.footnote_idx_dict[key] = []
        self.footnote_idx_dict[key].append(len(self.body))
        self.body.append('')  # dummy for replace later
        self.body.append('))')
        raise nodes.SkipNode

    def depart_footnote_reference(self, node):
        pass

    def visit_citation_reference(self, node):
        if not node.has_key('refid'):
            return
        self.in_citation_key = node['refid']

    def depart_citation_reference(self, node):
        self.body.append('((')
        if not self.citation_idx_dict.has_key(self.in_citation_key):
            self.citation_idx_dict[self.in_citation_key] = []
        self.citation_idx_dict[self.in_citation_key].append(len(self.body))
        self.body.append('')  # dummy footnote for replace later
        self.body.append('))')
        self.in_citation_key = None

    def visit_image(self, node):
        if node.has_key('uri'):
            self.body.append('<img src="%s"' % node['uri'])
            if node.has_key('alt'):
                self.body.append(' alt="%s"' % node['alt'])
            self.body.append('>')

    def depart_image(self, node):
        if not self.in_paragraph:
            self.body.append('\n')

    def visit_code_block(self, node):
        typ = node['type']
        self.body.append('>|%s|' % typ)
        self.body.append('\n')

    def depart_code_block(self, node):
        self.body.append('\n')
        self.body.append('||<')
        self.body.append('\n')
        self.body.append('\n')

    # ==================
    #  Hatena directives
    # ==================

    def visit_niconico(self, node):
        self.body.append("[niconico:%s]" % node["videoid"])

    def depart_niconico(self, node):
        self.body.append("\n")

    def visit_google(self, node):
        target = node["target"] + ":" if "target" in node else ""
        self.body.append("[google:%s]" % (target + node["query"]))

    def depart_google(self, node):
        if not self.in_paragraph:
            self.body.append("\n")

    def visit_amazon(self, node):
        self.body.append("[amazon:%s]" % node["query"])

    def depart_amazon(self, node):
        if not self.in_paragraph:
            self.body.append("\n")

    def visit_wikipedia(self, node):
        lang = node["lang"] + ":" if "lang" in node else ""
        self.body.append("[wikipedia:%s]" % (lang + node["query"]))

    def depart_wikipedia(self, node):
        if not self.in_paragraph:
            self.body.append("\n")

    def visit_twitter(self, node):
        type = ":" + node["type"] if "type" in node else ""
        self.body.append("[twitter:%s]" % (node["id"] + type))

    def depart_twitter(self, node):
        if not self.in_paragraph:
            self.body.append("\n")

    def visit_map(self, node):
        values = ["map", "x%sy%s" % (node["x"], node["y"])]
        if "type" in node:
            values.append(node["type"])
        if "width" in node:
            values.append("w%s" % (node["width"]))
        elif "height" in node:
            values.append("h%s" % (node["height"]))
        self.body.append(":".join(values))

    def depart_map(self, node):
        if not self.in_paragraph:
            self.body.append("\n")
