from docutils import nodes
import html4css1

class HTMLInlineTranslator(html4css1.HTMLTranslator):

    def astext(self):
        """Returns the inline HTML of the document."""
        return ''.join(self.body)

    def visit_bullet_list(self, node):
        """Simplified bullet lists."""
        self.body.append(self.starttag(node, 'ul'))

    def depart_bullet_list(self, node):
        """Simplified bullet lists."""
        self.body.append('</ul>\n')

    def visit_document(self, node):
        pass

    def depart_document(self, node):
        pass

    def visit_line_block(self, node):
        self.body.append(self.starttag(node, 'pre'))

    def visit_list_item(self, node):
        self.body.append(self.starttag(node, 'li', ''))

    def visit_literal_block(self, node):
        self.body.append(self.starttag(node, 'pre'))

    def visit_subtitle(self, node):
        self.body.append(self.starttag(node, 'h2', ''))

    # No more warnings in the output
    def visit_system_message(self, node):
        pass

    def depart_system_message(self, node):
        pass

    def visit_title(self, node):
        """Only 6 section levels are supported by HTML."""
        if isinstance(node.parent, nodes.topic):
            self.body.append(
                  self.starttag(node, 'p', ''))
            if node.parent.hasattr('id'):
                self.body.append(
                    self.starttag({}, 'a', '', name=node.parent['id']))
                self.context.append('</a></p>\n')
            else:
                self.context.append('</p>\n')
        elif isinstance(node.parent, nodes.sidebar):
            self.body.append(
                  self.starttag(node, 'p', ''))
            if node.parent.hasattr('id'):
                self.body.append(
                    self.starttag({}, 'a', '', name=node.parent['id']))
                self.context.append('</a></p>\n')
            else:
                self.context.append('</p>\n')
        elif self.section_level == 0:
            # document title
            self.head.append('<title>%s</title>\n'
                             % self.encode(node.astext()))
            self.body.append(self.starttag(node, 'h1', ''))
            self.context.append('</h1>\n')
        else:
            self.body.append(
                  self.starttag(node, 'h%s' % self.section_level, ''))
            atts = {}
            if node.parent.hasattr('id'):
                atts['name'] = node.parent['id']
            if node.hasattr('refid'):
                atts['href'] = '#' + node['refid']
            self.body.append(self.starttag({}, 'a', '', **atts))
            self.context.append('</a></h%s>\n' % (self.section_level))

    def depart_title(self, node):
        self.body.append(self.context.pop())

class Writer(html4css1.Writer):

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLInlineTranslator
