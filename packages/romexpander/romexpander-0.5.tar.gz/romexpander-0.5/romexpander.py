#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""romexpander.py

Usage:
    romexpander.py [options] [INPUT]
    romexpander.py [-h | --help]
    romexpander.py [-v | --version]

Arguments:
    INPUT                   optional input ROM file.

Options:
    -v, --version           show version info.
    -h, --help              show this message.
    -o, --output target     specify an output file.
    -t, --txt cfg           specify a config file.

"""

import md5
from binascii import unhexlify

from docopt import docopt


def get_md5(source):
    """Return the MD5 hash of the file `source`."""
    m = md5.new()
    while True:
        d = source.read(8196)
        if not d:
            break
        m.update(d)
    return m.hexdigest()


def hex_to_bstr(d):
    """Return the bytestring equivalent of a plain-text hex value."""
    if len(d) % 2:
        d = "0" + d
    return unhexlify(d)


def load_line(s):
    """Tokenize a tab-delineated string and return as a list."""
    return s.strip().split('\t')


def load_script(txt="ROM Expander Pro.txt"):
    script = {}
    script["file"] = txt
    with open(script["file"]) as script_file:
        script_lines = script_file.readlines()

    # Load the `NAME` line from script.
    l = load_line(script_lines.pop(0))
    assert 'NAME' == l.pop(0)
    script["source"], script["target"] = l
    assert script["target"] != script["source"]

    # Load the `SIZE` and optional `MD5`
    l = load_line(script_lines.pop(0))
    script["old_size"] = eval("0x" + l[1])
    script["new_size"] = eval("0x" + l[2])
    if l.index(l[-1]) > 2:
        script["MD5"] = l[3].lower()

    # Load the replacement `HEADER`.
    l = load_line(script_lines.pop(0))
    assert 'HEADER' == l.pop(0)
    script["header_size"] = eval("0x" + l.pop(0))
    assert script["header_size"] > len(l)
    # Sanitize and concatenate the header data.
    new_header = "".join(["0" * (2 - len(x)) + x for x in l])
    # Cast to character data and pad with 0x00 to header_size
    new_header = hex_to_bstr(new_header)
    script["header"] = new_header + "\x00" * (script["header_size"] - len(l))

    script["ops"] = []
    while script_lines:
        script["ops"].append(load_line(script_lines.pop(0)))

    script["patches"] = []
    for op in script["ops"]:
        if op[0] == "REPLACE":
            script["patches"].append(op[1:])
            script["ops"].remove(op)

    return script


def expand_rom(script):
    # Check the source file MD5.
    if "MD5" in script:
        with open(script["source"], "rb") as s_file:
            # Don't digest the header.
            s_file.read(script["header_size"])
            assert script["MD5"] == get_md5(s_file)
            print "MD5... match!"

    print "Expanding..."
    with open(script["source"], "rb") as s, open(script["target"], "wb") as t:
        def copy(s_offset, t_offset):
            source_ptr = script["header_size"] + s_offset
            write_ptr = script["header_size"] + t_offset
            s.seek(source_ptr)
            t.seek(write_ptr)
            t.write(s.read(end_ptr - write_ptr))

        def fill(destination, value):
            write_ptr = script["header_size"] + destination
            t.seek(write_ptr)
            t.write(value * (end_ptr - write_ptr))

        # Write Header
        t.write(script["header"])

        while script["ops"]:
            op = script["ops"].pop(0)
            cmd = op.pop(0)

            if not script["ops"]:
                end_ptr = script["header_size"] + script["new_size"]
            else:
                end_ptr = eval("0x" + script["ops"][0][1]) + \
                          script["header_size"]

            if cmd == "COPY":
                copy(eval("0x" + op[1]),  # Source
                     eval("0x" + op[0]))  # Target

            elif cmd == "FILL":
                fill(eval("0x" + op[0]),  # Destination
                     hex_to_bstr(op[1]))  # Value
            else:
                raise Exception

        # REPLACE
        for patch in script["patches"]:
            offset = eval("0x" + patch.pop(0))
            data = "".join(["0" * (2 - len(x)) + x for x in patch])
            t.seek(offset + script['header_size'])
            t.write(hex_to_bstr(data))

    print "Wrote %s successfully." % (script["target"])


def run(**kwargs):
    if kwargs['--txt']:
        script = load_script(kwargs['--txt'])
    else:
        script = load_script()
    if kwargs["--output"]:
        script["target"] = kwargs["--output"]
    if kwargs["INPUT"]:
        script["source"] = kwargs["INPUT"]
    expand_rom(script)

if __name__ == "__main__":
    arguments = docopt(__doc__, version='romexpander 0.4')
    run(**arguments)
