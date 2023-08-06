"""
detect.py

tries to detect if file is text file or not
"""

_text_characters = b'\n\r\t\f\b' + b''.join(chr(i) for i in xrange(32, 127))

def istextfile(filename, buffersize=512):
    """ taken from eli.thegreenplace.net """
    block = open(filename).read(buffersize)
    if not block:
        return True
    if b'\x00' in block:
        return False
    nontext = block.translate(None, _text_characters)
    return float(len(nontext)) / len(block) <= 0.30
