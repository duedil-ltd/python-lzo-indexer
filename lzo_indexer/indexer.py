import struct
from collections import namedtuple
from StringIO import StringIO

# Magic string expected at the start of the file to verify it's LZO
_LZO_MAGIC = bytearray("\x89LZO\x00\r\n\x1a\n")

_COMPRESSION_CHECKSUMS = (0x02, 0x200)  # ADLER32 CRC32
_DECOMPRESSION_CHECKSUMS = (0x01, 0x100)  # ADLER32 CRC32


def _parse_header(lzo_file):
    """Parse and verify the header of an LZO file, returning a tuple
    of the number of compressed/decompressed checksums expected at the
    end of each block.
    """

    if lzo_file.tell() != 0:
        raise Exception("File object must be at offset 0")

    # Parse the header
    if lzo_file.read(9) != _LZO_MAGIC:
        raise Exception("Invalid lzo file")

    # Ignore a bunch of values from the header
    # TODO: We should validate these
    lzop_version = lzo_file.read(2)
    library_version = lzo_file.read(2)
    extract_version = lzo_file.read(2)

    method = lzo_file.read(1)
    level = lzo_file.read(1)

    # Checksum flags
    flags, = struct.unpack(">I", lzo_file.read(4))

    num_compressed_checksums = 0
    for idx, flag in enumerate(_COMPRESSION_CHECKSUMS):
        if (flag & flags) != 0:
            num_compressed_checksums += 1

    num_decompressed_checksums = 0
    for idx, flag in enumerate(_DECOMPRESSION_CHECKSUMS):
        if (flag & flags) != 0:
            num_decompressed_checksums += 1

    # Parse out the mode/mtime/gmtdiff values we're not interested in
    mode = lzo_file.read(4)
    mtime = lzo_file.read(4)
    gmtdiff = lzo_file.read(4)

    # Extract the filename
    filename_length = ord(lzo_file.read(1))
    if filename_length > 0:
        filename = str(lzo_file.read(filename_length))

    # TODO: Verify the header checksum against these bytes
    lzo_file.read(4)

    # Process extra header field for lzo < 1.08. This is a checksum that
    # needs to also be validated
    if (flags & 0x00000040) != 0:
        size, = struct.unpack(">I", lzo_file.read(4))
        if size > 0:
            lzo_file.read(size)
        lzo_file.read(4)

    return num_compressed_checksums, num_decompressed_checksums


def get_lzo_blocks(lzo_file):
    """Return a generator containing all of the block offsets for each
    compressed block of data in the LZO file.
    """

    num_compressed_chksms, num_decompressed_chksms = _parse_header(lzo_file)

    while True:
        decompressed_blocksize, = struct.unpack(">I", lzo_file.read(4))
        if decompressed_blocksize == 0:
            break

        compressed_blocksize, = struct.unpack(">I", lzo_file.read(4))

        num_chksms_to_skip = num_decompressed_chksms
        if decompressed_blocksize == compressed_blocksize:
            num_chksms_to_skip += num_compressed_chksms

        skip = 4 * num_chksms_to_skip

        position = lzo_file.tell()

        block_start = position - 8  # Rewind back to before the block headers
        next_block = position + compressed_blocksize + skip

        yield block_start

        lzo_file.seek(next_block)  # Seek to the next block


def index_lzo_string(string):
    """Return a generator containing block offsets for each compressed block
    of data in the LZO string.
    """

    index = StringIO()
    index_lzo_file(StringIO(string), index)

    return index.getvalue()


def index_lzo_file(lzo_file, index_file):
    """Index the given LZO file and write the index to the given output stream.
    """

    for block_offset in get_lzo_blocks(lzo_file):
        index_file.write(struct.pack(">Q", block_offset))

    return index_file
