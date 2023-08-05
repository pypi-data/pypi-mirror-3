def prefix():

    return 8 * ' '

import unittest
import processor
class TestProcessor(unittest.TestCase):
# TODO: figure out why this cannot be after "process"


    def test_function_=_['def_foo():',_"____a_=_4",_"____return_'foo'"](self):
        c = processor.SpecificationProcessor('processor')

def process(c, line):

    return c.process_line('    ' + line)


    def test_processes_empty_lines(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process(['', '']), '')

    def test_processes_function_with_return(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process(function), "def foo():\n    a = 4\n    return 'foo'")

    def test_skips_def(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('def foo():'), 'def foo():')

    def test_skips_return(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line(prefix() + 'return True'), prefix() + 'return True')

    def test_processes_declaration(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('process this  '), '\n    ' + 'def test_process_this(self):')

    def test_processes_indentation(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'a = 5'), prefix() + 'a = 5')

    def test_processes_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b==10'), prefix() + 'self.assertEqual(b, 10)')

    def test_processes_not_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b != 10'), prefix() + 'self.assertNotEqual(b, 10)')

    def test_processes_almost_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b ~= 10'), prefix() + 'self.assertAlmostEqual(b, 10)')

    def test_processes_not_almost_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b !~= 10'), prefix() + 'self.assertNotAlmostEqual(b, 10)')

    def test_processes_bigger_than(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b > 5'), prefix() + 'self.assertTrue(b > 5)')

    def test_processes_bigger_than_or_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b >= 5'), prefix() + 'self.assertTrue(b >= 5)')

    def test_processes_smaller_than(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b < 5'), prefix() + 'self.assertTrue(b < 5)')

    def test_processes_smaller_than_or_equals(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'b <= 5'), prefix() + 'self.assertTrue(b <= 5)')

    def test_processes_multiple_inqualities(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, '4 < b < 10'), prefix() + 'self.assertTrue(4 < b < 10)')
        self.assertEqual(process(c, '4 <= b < 10'), prefix() + 'self.assertTrue(4 <= b < 10)')
        self.assertEqual(process(c, '4 < b <= 10'), prefix() + 'self.assertTrue(4 < b <= 10)')
        self.assertEqual(process(c, '4 <= b <= 10'), prefix() + 'self.assertTrue(4 <= b <= 10)')

    def test_processes_empty_line(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, '    '), '')

    def test_processes_newline(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, '\n'), '')

    def test_processes_comment(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('# my comment'), '# my comment')
        self.assertEqual(c.process_line('    # my comment'), '    # my comment')

    def test_processes_raises(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(process(c, 'a raises TypeError'), prefix() + 'try:a \n        except TypeError: pass')

    def test_processes_anything(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('some test'), '\n    def test_some_test(self):')
        self.assertEqual(c.process_line('foobar'), '    foobar')
        self.assertEqual(c.process_line(''), '')
        self.assertEqual(c.process_line('other test'), '\n    def test_other_test(self):')
        self.assertEqual(c.process_line(''), '')
        self.assertEqual(c.process_line('yet another test'), '\n    def test_yet_another_test(self):')

    def test_processes_test_with_Python(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('some test'), '\n    def test_some_test(self):')
        self.assertEqual(c.process_line('    if True:'), '        if True:')
        self.assertEqual(c.process_line("        print('works')"), "            print('works')")
        self.assertEqual(c.process_line(''), '')
        self.assertEqual(c.process_line("    print('end')"), "        print('end')")

    def test_processes_long_string(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('some test'), '\n    def test_some_test(self):')
        self.assertEqual(c.process_line("    expected = '''"), "        expected = '''")
        self.assertEqual(c.process_line('var a = 4;'), 'var a = 4;')
        self.assertEqual(c.process_line('var b = 5;'), 'var b = 5;')
        self.assertEqual(c.process_line("'''"), "'''")
        self.assertEqual(c.process_line(''), '')
        self.assertEqual(c.process_line("    print('done')"), "        print('done')")

    def test_processes_comment_at_beginning(self):
        c = processor.SpecificationProcessor('processor')

        self.assertEqual(c.process_line('#some comment'), '#some comment')
        self.assertEqual(c.process_line(''), '')
suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessor)
unittest.TextTestRunner(verbosity=2).run(suite)