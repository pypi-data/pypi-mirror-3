import sys
import unittest
import textwrap
import docutils.core
import docutils.nodes
import docutils.writers


if sys.version_info >= (3, 0):
    py3 = True
else:
    py3 = False


WRITER_ALIASES = {
    'textile': 'docutils_textile',
}


class ReSTTestCase(unittest.TestCase):
    def __init__(self, _from, _to, source, expect, actual, node_tree):
        unittest.TestCase.__init__(self)
        self.source = source
        self.expect = expect
        self.actual = actual
        self.node_tree = node_tree
        self._from = _from
        self._to = _to

    def runTest(self):
        message = textwrap.dedent("""\
        Convertion Mismatch (%s -> %s)
        ##source:
        %s

        ##expect:
        %s

        ##actual:
        %s

        ##node-tree:
        %s
        """)
        message = message % (self._from, self._to, self.source, self.expect, self.actual, self.node_tree)
        self.assertEqual(self.expect, self.actual, message)


class DocutilsTestTranslator(docutils.nodes.NodeVisitor):

    def __init__(self, document):
        docutils.nodes.NodeVisitor.__init__(self, document)
        self.body = []

    def unknown_visit(self, node):
        pass

    def unknown_departure(self, node):
        pass

    def visit_container(self, node):
        if 'classes' in node and 'test' in node['classes']:
            literals = [x for x in node.children if x.tagname=='literal_block']
            if len(literals) < 2:
                raise RuntimeError('Need 2 literal-block elements "from", "to"')

            _, _from, _to = node['classes'][:3]
            _to = WRITER_ALIASES.get(_to, _to)
            source_node, expect_node = literals[:2]  #discard over 2 nodes.
            source = source_node.astext()
            expect = expect_node.astext()
            actual = docutils.core.publish_string(
                    source,
                    parser_name=_from,
                    writer_name=_to,
                    settings_overrides={'output_encoding': 'unicode'})
            actual = actual.strip()
            node_tree = docutils.core.publish_string(
                    source,
                    parser_name=_from,
                    writer_name="pseudoxml").strip()
            self.body.append(ReSTTestCase(
                _from, _to, source, expect, actual, node_tree))

        raise docutils.nodes.SkipNode


class DocutilsTestWriter(docutils.writers.Writer):
    def translate(self):
        visitor = DocutilsTestTranslator(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.body


class ReSTTestSuite(unittest.TestSuite):

    def __init__(self, filename):
        f = open(filename, 'rt')
        data = f.read()
        if not py3:
            data = data.decode('utf8')
        tests = docutils.core.publish_string(
                source=data, source_path=f.name,
                writer=DocutilsTestWriter())
        f.close()
        unittest.TestSuite.__init__(self, tests)


def suite():
    suite = ReSTTestSuite('README.rst')
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
