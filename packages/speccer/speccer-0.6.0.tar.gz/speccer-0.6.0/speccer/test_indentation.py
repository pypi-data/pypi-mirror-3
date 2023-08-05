import unittest
import indentation
class TestIndentation(unittest.TestCase):

    def test_renders_indentation(self):
        i = indentation.Indentation('    foobar')
        self.assertEqual(i(), '    ')

    def test_fails_on_number(self):
        try:i = indentation.Indentation(3) 
        except TypeError: pass
suite = unittest.TestLoader().loadTestsFromTestCase(TestIndentation)
unittest.TextTestRunner(verbosity=2).run(suite)