def test_converter(to, format=None, extra_args=()):

    def reader(*args):

        pass

import unittest
import pypandoc
class TestPypandoc(unittest.TestCase):
    def processor(*args):

        return 'ok'

        source = 'foo'
    return _convert(reader, processor, source, to, format, extra_args)


    def test_converts_valid_format(self):
        self.assertEqual(test_converter(format='md', to='rest'), 'ok')

    def test_does_not_convert_to_invalid_format(self):
        try:test_converter(format='md', to='invalid') 
        except RunTimeError: pass

    def test_does_not_convert_from_invalid_format(self):
        try:test_converter(format='invalid', to='rest') 
        except RunTimeError: pass
suite = unittest.TestLoader().loadTestsFromTestCase(TestPypandoc)
unittest.TextTestRunner(verbosity=2).run(suite)