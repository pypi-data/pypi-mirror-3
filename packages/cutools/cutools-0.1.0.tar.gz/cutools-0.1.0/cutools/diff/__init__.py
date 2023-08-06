from hashlib import md5
from clint.textui import puts, colored


def clean_diff(diff):
    """Removes diff header from a diff.
    """
    res = []
    skip = True
    for line in diff.split('\n'):
        if line.startswith('diff --git'):
            skip = True
        if line.startswith('@@ '):
            skip = False
        if not skip:
            res.append(line)
    return '\n'.join(res)


def print_diff(diff):
    """Prints colored diff.
    """
    for line in diff.split('\n'):
        line = unicode(line).encode('utf-8')
        if line.startswith('+'):
            puts(colored.green(line))
        elif line.startswith('-'):
            puts(colored.red(line))
        else:
            puts(line)


def get_chunks(diff):
    """Returns a list with all the chunks in this diff.
    """
    diff = clean_diff(diff)
    chunk = []
    chunks = []
    for line in diff.split('\n'):
        if not line:
            continue
        if line.startswith('@@ '):
            if chunk:
                chunks.append('\n'.join(chunk))
            chunk = [line]
        else:
            chunk.append(line)
    if chunk:
        chunks.append('\n'.join(chunk))
    return chunks


def get_hashed_chunks(chunks):
    chunks_dict = {}
    for chunk in chunks:
        chunks_dict[md5(unicode(chunk).encode('utf-8')).hexdigest()] = chunk
    return chunks_dict


def clean_chunk(chunk):
    """Clean headers from chunk.
    """
    return '\n'.join([x[1:] for x in chunk.split('\n')
                      if x and x[0] not in ('-', '@')])


def chunk_in_text(chunk, text):
    """Checks if chunk is inside text.
    """
    chunk = clean_chunk(chunk)
    return text.find(chunk) >= 0
