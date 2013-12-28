import unittest
import lzo_indexer
from StringIO import StringIO
from subprocess import Popen, PIPE, STDOUT


class TestLZOIndexer(unittest.TestCase):

    def test_get_blocks_single_block(self):
        stream = self._lzo_stream(1)
        index = lzo_indexer.get_lzo_blocks(stream)

        block = index.next()
        self.assertEqual(block, 38)
        with self.assertRaises(StopIteration):
            index.next()

    def test_get_blocks_multiple_blocks(self):
        stream = self._lzo_stream(10**6)
        index = lzo_indexer.get_lzo_blocks(stream)

        expected_offsets = [38, 1233, 2428, 3623]
        self.assertEqual(list(index), expected_offsets)

    def test_index_lzo_string_single_block(self):
        string = self._lzo_stream(1).getvalue()
        index = lzo_indexer.index_lzo_string(string)

        self.assertEqual(index, "\x00\x00\x00\x00\x00\x00\x00\x26")

    def test_index_lzo_string_multiple_blocks(self):
        string = self._lzo_stream(10**6).getvalue()
        index = lzo_indexer.index_lzo_string(string)

        self.assertEqual(index, "\x00\x00\x00\x00\x00\x00\x00&\x00\x00\x00" \
                                "\x00\x00\x00\x04\xd1\x00\x00\x00\x00\x00" \
                                "\x00\t|\x00\x00\x00\x00\x00\x00\x0e'")

    def test_index_lzo_file_single_block(self):
        stream = self._lzo_stream(1)
        index = StringIO()

        lzo_indexer.index_lzo_file(stream, index)

        self.assertEqual(index.getvalue(), "\x00\x00\x00\x00\x00\x00\x00\x26")

    def test_index_lzo_file_multiple_blocks(self):
        stream = self._lzo_stream(10**6)
        index = StringIO()

        lzo_indexer.index_lzo_file(stream, index)

        self.assertEqual(index.getvalue(), "\x00\x00\x00\x00\x00\x00\x00&\x00" \
                                           "\x00\x00\x00\x00\x00\x04\xd1\x00" \
                                           "\x00\x00\x00\x00\x00\t|\x00\x00" \
                                           "\x00\x00\x00\x00\x0e'")

    def _lzo_stream(self, length=4096):
        """Compress a string of null bytes, the length being defined by the
        argument to this function.
        """

        compressor = Popen(["lzop", "-c"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = compressor.communicate(input="\x00" * length)

        if stderr:
            raise Exception("Failed to compress with error %r" % (stderr))

        stream = StringIO(stdout)
        stream.seek(0)

        return stream
