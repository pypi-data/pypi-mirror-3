# -*- coding: utf-8 -*-
from docutils import nodes
from sphinx.util.compat import Directive


class s6_node(nodes.raw): pass


class S6(Directive):
    """
    A s6 entry, control s6 slide effects, actions and styles.
    """

    has_content = True
    required_arguments = 1
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {}

    def run(self):
        env = self.state.document.settings.env
        event = self.arguments[0]
        if len(self.arguments) == 2:
            contents = self.arguments[1]
        else:
            contents = '\n'.join(self.content)

        if event == 'effect':
            if contents not in ('slide', 'fade', 'fadeScale', 'fadeScaleFromUp', 'fadeScaleFromUpTransparent'):
                raise RuntimeError('Unknown effect type: %r' % contents)
            contents = "'%s'" % contents
        elif event == 'actions':
            contents = "[%s]" % contents.strip().strip(',')
        elif event == 'styles':
            contents = "{%s}" % contents.strip().strip(',')
        else:
            raise RuntimeError('Unknown event name: %r' % event)

        text = """if(typeof s6 != 'undefined'){s6.page({%s: %s});}""" % (event, contents)
        node = s6_node(text)

        if 'class' in self.options:
            node['classes'] += options['class']

        return [node]


def visit_s6_node(self, node):
    self.body.append(self.starttag(node, 'script'))
    self.body.append(node.rawsource)
    self.set_first_last(node)


def depart_s6_node(self, node=None):
    self.body.append('</script>\n')


def setup(app):
    app.add_node(s6_node, html=(visit_s6_node, depart_s6_node))

    app.add_directive('s6', S6)


