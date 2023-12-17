inputs = [
    r"""
        true
    """,
    r"""
        false
    """,
    r"""
        null
    """,
    r"""
        "hello"
    """,
    r"""
        -5
    """,
    r"""
        5
    """,
    r"""
        0
    """,
    r"""
        { }
    """,
    r"""
        [ 22.0e+02, "+,-./0:E[]bnstu{}\b\f\t", 1100, 100.01, -0.2e00 ]
    """,
    r"""
        { "":43, "fo\u006Fo" : 41E2, "":"", "":[],
          "\uAAAA\uEEEE\uaaaa\ubbbb\ueeee\uffff\u0000\u111101":true, "":false, "":null, "":{} }
    """,
    r"""
        [ -21, -32e+3, 2.3E-1, {"":true},
            {"":false}, {"":null}, 0.20e0
        ]
    """,
    r"""
        [ [true], [false], [{"":-1}], {"":[]} ]
    """,
    r"""
        [
            [ "hello\u0020world\r\n" ],
            null,    true,     false,
            [                    ],
            [ "\/\\hello \"world\""  ],
            [ null, 123, "hllo", 0, {"":0.00}, [0E-0] ],
            { "a" : {
                "x": "y",
                "z": -1.5,
                "w": 12e3,
                "q": 0e1
            }},
            true
        ]
    """,
]

def main():
    chart = set()
    for input in inputs:
        print parse_string(input, chart)
    v = len(chart)
    t = 0
    for row in states:
        t += sum(0 if code & 255 == 0xFF else 1 for code in row)
    print "{} states, visited {}, verification {:d}%".format(t, v, int(100.0*v/t))

    for state, row in enumerate(states):
        for cat, code in enumerate(row):
            if code & 255 != 0xFF and (state, cat) not in chart:
                print "not visited:", hex(state), hex(cat), repr("".join(chr(g) for g, cc in enumerate(catcode) if cc == cat)), hex(code)

def parse_string(string, chart):
    stack = []
    state = 0x00
    ds = [] # data stack
    ss = [] # string stack
    es = [] # escape stack
    for ch in string:
        cat = catcode[min(ord(ch), 0x7E)]
        state = parse_ch(cat, ch, stack, state, ds, ss, es, chart)
    state = parse_ch(catcode[32], u'', stack, state, ds, ss, es, chart)
    if state != 0x00:
        raise Exception("JSON decode error: truncated")
    if len(ds) != 1:
        raise Exception("JSON decode error: too many objects")
    return ds.pop()

def parse_ch(cat, ch, stack, state, ds, ss, es, chart):
    while True:
        code = states[state][cat]
        action = code >> 8 & 0xFF
        code   = code      & 0xFF
        if action == 0xFF and code == 0xFF:
            raise Exception("JSON decode error: syntax")
        elif action >= 0x80: # shift
            stack.append(gotos[state])
            action -= 0x80
        if action > 0:
            do_action(action, ch, ds, ss, es)
        if code == 0xFF:
            state = stack.pop()
        else:
            chart.add((state, cat))
            state = code
            return state
    return state

def do_action(action, ch, ds, ss, es):
    if action == 0x1:
        ds.append([])
    elif action == 0x2:
        ds.append({})
    elif action == 0x3:
        val = ds.pop()
        ds[len(ds)-1].append(val)
    elif action == 0x4:
        val = ds.pop()
        key = ds.pop()
        ds[len(ds)-1][key] = val
    elif action == 0x5:
        ds.append(None)
    elif action == 0x6:
        ds.append(True)
    elif action == 0x7:
        ds.append(False)
    elif action == 0x8:
        val = u"".join(ss)
        ds.append(val)
        ss[:] = []
        es[:] = []
    elif action == 0x9:
        val = int(u"".join(ss))
        ds.append(val)
        ss[:] = []
    elif action == 0xA:
        val = float(u"".join(ss))
        ds.append(val)
        ss[:] = []
    elif action == 0xB:
        ss.append(ch)
    elif action == 0xC:
        es.append(ch)
    elif action == 0xD:
        ss.append(unichr(escape_characters[ch]))
    elif action == 0xE:
        ss.append(unichr(int(u"".join(es), 16)))
        es[:] = []
    else:
        assert False, "JSON decoder bug"

def read_file(filename):
    with open(filename, "rb") as fd:
        return fd.read().decode('utf-8')

states = [
    [ 0xffff, 0x0000, 0x801a, 0xffff, 0xffff, 0x8b29, 0xffff, 0xffff, 0x8b28, 0x8b22, 0xffff, 0xffff, 0xffff, 0x810e, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x8009, 0xffff, 0x8001, 0xffff, 0xffff, 0x8005, 0xffff, 0x8212, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0002, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0003, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0004, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, 0x05ff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0006, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0007, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0008, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, 0x06ff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x000a, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x000b, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x000c, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x000d, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, 0x07ff, ],
    [ 0xffff, 0x000e, 0x801a, 0xffff, 0xffff, 0x8b29, 0xffff, 0xffff, 0x8b28, 0x8b22, 0xffff, 0xffff, 0xffff, 0x810e, 0xffff, 0x0011, 0xffff, 0xffff, 0xffff, 0x8009, 0xffff, 0x8001, 0xffff, 0xffff, 0x8005, 0xffff, 0x8212, 0xffff, ],
    [ 0xffff, 0x000f, 0xffff, 0xffff, 0x0310, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0311, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0x0010, 0x801a, 0xffff, 0xffff, 0x8b29, 0xffff, 0xffff, 0x8b28, 0x8b22, 0xffff, 0xffff, 0xffff, 0x810e, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x8009, 0xffff, 0x8001, 0xffff, 0xffff, 0x8005, 0xffff, 0x8212, 0xffff, ],
    [ 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, ],
    [ 0xffff, 0x0012, 0x801a, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0019, ],
    [ 0xffff, 0x0013, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0014, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0x0014, 0x801a, 0xffff, 0xffff, 0x8b29, 0xffff, 0xffff, 0x8b28, 0x8b22, 0xffff, 0xffff, 0xffff, 0x810e, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x8009, 0xffff, 0x8001, 0xffff, 0xffff, 0x8005, 0xffff, 0x8212, 0xffff, ],
    [ 0xffff, 0x0015, 0xffff, 0xffff, 0x0416, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0419, ],
    [ 0xffff, 0x0016, 0x801a, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0x0017, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0018, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0x0018, 0x801a, 0xffff, 0xffff, 0x8b29, 0xffff, 0xffff, 0x8b28, 0x8b22, 0xffff, 0xffff, 0xffff, 0x810e, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x8009, 0xffff, 0x8001, 0xffff, 0xffff, 0x8005, 0xffff, 0x8212, 0xffff, ],
    [ 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, 0x00ff, ],
    [ 0x0b1a, 0x0b1a, 0x0021, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x001b, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, 0x0b1a, ],
    [ 0xffff, 0xffff, 0x0b1a, 0xffff, 0xffff, 0xffff, 0xffff, 0x0b1a, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0b1a, 0xffff, 0xffff, 0x0d1a, 0xffff, 0x0d1a, 0xffff, 0x0d1a, 0x0d1a, 0xffff, 0x0d1a, 0x801c, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0c1d, 0x0c1d, 0xffff, 0x0c1d, 0x0c1d, 0xffff, 0xffff, 0xffff, 0x0c1d, 0x0c1d, 0x0c1d, 0x0c1d, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0c1e, 0x0c1e, 0xffff, 0x0c1e, 0x0c1e, 0xffff, 0xffff, 0xffff, 0x0c1e, 0x0c1e, 0x0c1e, 0x0c1e, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0c1f, 0x0c1f, 0xffff, 0x0c1f, 0x0c1f, 0xffff, 0xffff, 0xffff, 0x0c1f, 0x0c1f, 0x0c1f, 0x0c1f, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0c20, 0x0c20, 0xffff, 0x0c20, 0x0c20, 0xffff, 0xffff, 0xffff, 0x0c20, 0x0c20, 0x0c20, 0x0c20, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, 0x0eff, ],
    [ 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, 0x08ff, ],
    [ 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x0b23, 0x09ff, 0x0b22, 0x0b22, 0x09ff, 0x09ff, 0x0b25, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x0b25, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0b24, 0x0b24, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0b24, 0x0b24, 0x0aff, 0x0aff, 0x0b25, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0b25, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, ],
    [ 0xffff, 0xffff, 0xffff, 0x0b26, 0xffff, 0x0b26, 0xffff, 0xffff, 0x0b27, 0x0b27, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0b27, 0x0b27, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
    [ 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0b27, 0x0b27, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, 0x0aff, ],
    [ 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x0b23, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x0b25, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x0b25, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, 0x09ff, ],
    [ 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0x0b28, 0x0b22, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, 0xffff, ],
]
gotos = [0, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 15, 255, 15, 255, 19, 255, 21, 255, 23, 255, 21, 255, 255, 26, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]
catcode = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 10, 0, 0, 0, 0, 0, 0, 11, 11, 11, 11, 12, 11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 13, 14, 15, 0, 0, 0, 16, 17, 11, 11, 18, 19, 0, 0, 0, 0, 0, 20, 0, 21, 0, 0, 0, 22, 23, 24, 25, 0, 0, 0, 0, 0, 26, 0, 27, 0]

escape_characters = {'b': 8, 't': 9, 'n': 10, 'f': 12, 'r': 13}

if __name__=="__main__":
    main()
