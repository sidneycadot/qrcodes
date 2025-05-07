#! /usr/bin/env python3

def generate_bytes_with_length(n: int):
    if n == 0:
        yield bytes()
    else:
        for hd in range(256):
            for tl in generate_bytes_with_length(n - 1):
                yield bytes([hd]) + tl


def generate_bytes():
    len = 0
    while True:
        yield from generate_bytes_with_length(len)
        len += 1

q = 0
for bb in generate_bytes_with_length(2):
    try:
        su = bb.decode('utf-8')
    except UnicodeDecodeError:
        continue
    si = bb.decode('iso-8859-1')
    if su != si:
        ru = repr(su)
        ri = repr(si)
        if not (("\\x" in ru) or ("\\u" in ru) or ("\\x" in ri)):
            assert len(si) >= len(su)
            if len(su) == 1:
                print(q, repr(bb), ru, ri)
                q += 1