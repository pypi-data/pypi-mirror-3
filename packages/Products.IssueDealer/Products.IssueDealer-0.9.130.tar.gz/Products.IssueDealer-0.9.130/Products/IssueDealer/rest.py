##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Structured Text Renderer Classes"""

import string
from htmllib import HTMLParser
from formatter import AbstractFormatter, NullWriter, AbstractWriter

class StringWriter(NullWriter):

    def __init__(self, maxcol=59):
        self.data = ''
        self.font = None
        self.styles = []
        self.maxcol = maxcol
        self.margin = ('BASE', 0)
        NullWriter.__init__(self)
        self.reset()
        
    def reset(self):
        self.data = ''
        self.col = 0
        self.atbreak = 0

    def send_paragraph(self, blankline):
        self.data += '\n'*blankline
        self.col = 0
        self.atbreak = 0

    def send_line_break(self):
        self.data += '\n'
        self.col = 0
        self.atbreak = 0

    def send_hor_rule(self, *args, **kw):
        self.data += '\n'
        self.data += '----'
        self.data += '\n\n'
        self.col = 0
        self.atbreak = 0

    def send_literal_data(self, data):
        self.data += data
        i = data.rfind('\n')
        self.col = self.col + len(data)
        self.atbreak = 0

    def send_flowing_data(self, data):
        if not data: return
        atbreak = self.atbreak or data[0] in string.whitespace
        col = self.col
        if col == 0 or atbreak:
            self.data += ' '*self.margin[1]*4
            col = self.margin[1]*4
        maxcol = self.maxcol
        maxline = 0
        for word in data.split():
            if atbreak:
                if col + len(word) >= maxcol:
                    self.data += '\n'
                    if col + len(word) > maxline: maxline = col + len(word)
                    col = 0
                    if self.margin[1] > 0:
                        self.data += ' '*self.margin[1]*4
                        col = self.margin[1]*4
                else:
                    self.data += ' '
                    col = col + 1
            self.data += word
            col = col + len(word)
            if col > maxline: maxline = col
            atbreak = 1
        self.col = col
        self.atbreak = data[-1] in string.whitespace
        if self.styles != []:
            if self.styles[-1][0] == 'underline':
                self.data += '\n'
                self.data += self.styles[-1][1]*maxline
                self.data += '\n'
                del self.styles[-1]

    def send_label_data(self, data):
        if (self.margin[1]-1)*4 > 0:
            self.data += ' '*((self.margin[1]-1)*4)
            self.col += (self.margin[1]-1)*4
        self.data += data
        if len(data) < 4:
            self.data += ' '*(4-len(data))
            self.col += 4
        else:
            self.col += len(data)

    def new_margin(self, margin, level):
        self.margin = (margin, level)

    def new_styles(self, style):
        self.styles.append(style)


class ReSTFormatter(AbstractFormatter):

    def __init__(self, writer):
        AbstractFormatter.__init__(self, writer)
        self.margins = [('BASE', 0), ]
        self.inlines = []

    def push_style(self, style):
        self.writer.new_styles(style)

    def push_inline(self, inline):
        self.writer.send_flowing_data(inline)
        self.inlines.append(inline)

    def pop_inline(self):
        self.writer.send_flowing_data(self.inlines.pop() + ' ')

    def push_margin(self, margin):
        level = self.margins[-1][1] + 1
        self.margins.append((margin, level))
        self.writer.new_margin(margin, level)

    def pop_margin(self):
        del self.margins[-1]
        self.writer.new_margin(self.margins[-1][0], self.margins[-1][1])

    def add_line_break(self):
        if not (self.hard_break or self.para_end):
            inlines = self.inlines[:]
            inlines.reverse()
            for inline in inlines:
                self.writer.send_flowing_data(inline)
            self.writer.send_line_break()
            for inline in self.inlines:
                self.writer.send_flowing_data(inline)
            self.have_label = self.parskip = 0
        self.hard_break = self.nospace = 1
        self.softspace = 0


class HTMLParserForReST(HTMLParser):

    def close(self):
        """Doing my own post processing:
        
           * Building linklist
        """
        HTMLParser.close(self)
        
        self.formatter.end_paragraph(2)
        for url in self.anchorlist:
            self.handle_data(".. _`%s`: %s" % (url[0], url[1]))
            self.formatter.add_line_break()


    def do_br(self, attrs):
        HTMLParser.do_br(self, attrs)

    
    def start_h1(self, attr):
        self.formatter.push_style(('underline', '='))

    def start_h2(self, attr):
        self.formatter.push_style(('underline', '-'))

    def start_h3(self, attr):
        self.formatter.push_style(('underline', '~'))

    def start_h4(self, attr):
        self.formatter.push_style(('underline', '"'))

    def start_h6(self, attr):
        self.formatter.push_style(('underline', '#'))

    def do_hr(self, attr):
        self.formatter.add_hor_rule()

    def start_p(self, attr):
        pass

    def end_p(self):
        self.formatter.end_paragraph(1)

    def start_ul(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_margin('ul')
        self.list_stack.append(['ul', '*', 0])

    def end_ul(self):
        if self.list_stack: del self.list_stack[-1]
        self.formatter.pop_margin()
        self.formatter.end_paragraph(1)

    def start_ol(self, attrs):
        self.formatter.end_paragraph(1)
        self.formatter.push_margin('ol')
        label = '1.'
        for a, v in attrs:
            if a == 'type':
                if len(v) == 1: v = v + '.'
                label = v
        self.list_stack.append(['ol', label, 0])

    def end_ol(self):
        if self.list_stack: del self.list_stack[-1]
        self.formatter.pop_margin()
        self.formatter.end_paragraph(1)

    def start_dl(self, attrs):
        self.formatter.end_paragraph(1)
        self.list_stack.append(['dl', '', 0])

    def end_dl(self):
        self.formatter.end_paragraph(1)
        if self.list_stack: del self.list_stack[-1]

    def start_dt(self, attrs):
        pass

    def end_dt(self):
        self.formatter.push_margin('dd')
        self.formatter.add_line_break()

    def start_dd(self, attrs):
        self.list_stack.append(['dd', '', 0])
        
    def end_dd(self):
        self.formatter.pop_margin()
        self.formatter.add_line_break()
        if self.list_stack:
            if self.list_stack[-1][0] == 'dd':
                del self.list_stack[-1]

    def start_blockquote(self, attrs):
        self.formatter.push_margin('blockquote')
        self.formatter.end_paragraph(1)

    def end_blockquote(self):
        self.formatter.pop_margin()
        self.formatter.end_paragraph(1)

    def start_i(self, attr):
        self.formatter.push_inline('*')

    def end_i(self):
        self.formatter.pop_inline()

    def start_b(self, attr):
        self.formatter.push_inline('**')

    def end_b(self):
        self.formatter.pop_inline()

    def anchor_bgn(self, href, name, type):
        self.anchor = href
        self.save_bgn()

    def anchor_end(self):
        if self.anchor:
            text = self.save_end()
            self.handle_data("`%s`_" % text)
            self.anchorlist.append((text, self.anchor))
            self.anchor = None


def qtemplate(text):
    lines = text.split("\n")
    text = ''
    for line in lines:
        text += '' + line + '\n'
    return text

def html_to_rest(data):
    writer = StringWriter()
    parser = HTMLParserForReST(ReSTFormatter(writer))
    parser.feed(clean(data))
    parser.close()
    return writer.data.replace('\n****\n', '').replace('\n**\n', '')
