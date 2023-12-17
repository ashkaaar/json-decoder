def sskip(table):
    table.update(
        {
            " ": 0x00FE,
            "\t": 0x00FE,
            "\r": 0x00FE,
            "\n": 0x00FE,
        }
    )
    return table


def pval(table):
    table.update(
        {
            "n": 0x8010,
            "t": 0x8020,
            "f": 0x8030,
            "[": 0x8140,
            "{": 0x8250,
            '"': 0x8060,
            "0": 0x8B76,
            "1": 0x8B70,
            "2": 0x8B70,
            "3": 0x8B70,
            "4": 0x8B70,
            "5": 0x8B70,
            "6": 0x8B70,
            "7": 0x8B70,
            "8": 0x8B70,
            "9": 0x8B70,
            "-": 0x8B78,
        }
    )
    return sskip(table)


def hexv(table, cmd):
    for ch in "0123456789abcdefABCDEF":
        table[ch] = cmd
    return table


states = {
    0x00: pval({}),
    0x10: {"u": 0x11},
    0x11: {"l": 0x12},
    0x12: {"l": 0x13},
    0x13: {"": 0x05FF},
    0x20: {"r": 0x21},
    0x21: {"u": 0x22},
    0x22: {"e": 0x23},
    0x23: {"": 0x06FF},
    0x30: {"a": 0x31},
    0x31: {"l": 0x32},
    0x32: {"s": 0x33},
    0x33: {"e": 0x34},
    0x34: {"": 0x07FF},
    0x40: pval({"]": 0x4F}),
    0x41: sskip({",": 0x0342, "]": 0x034F}),
    0x42: pval({}),
    0x4F: {"": 0x00FF},
    0x50: sskip({'"': 0x8060, "}": 0x005F}),
    0x51: sskip({":": 0x52}),
    0x52: pval({}),
    0x53: sskip({",": 0x0454, "}": 0x045F}),
    0x54: sskip({'"': 0x8060}),
    0x55: sskip({":": 0x56}),
    0x56: pval({}),
    0x5F: {"": 0x00FF},
    0x60: {'"': 0x6F, "": 0x0B60, "\\": 0x61},
    0x61: {
        '"': 0x0B60,
        "\\": 0x0B60,
        "/": 0x0B60,
        "b": 0x0D60,
        "f": 0x0D60,
        "n": 0x0D60,
        "r": 0x0D60,
        "t": 0x0D60,
        "u": 0x8062,
    },
    0x62: hexv({}, 0x0C63),
    0x63: hexv({}, 0x0C64),
    0x64: hexv({}, 0x0C65),
    0x65: hexv({}, 0x0C66),
    0x66: {"": 0x0EFF},
    0x6F: {"": 0x08FF},
    0x70: {
        "0": 0x0BFE,
        "1": 0x0BFE,
        "2": 0x0BFE,
        "3": 0x0BFE,
        "4": 0x0BFE,
        "5": 0x0BFE,
        "6": 0x0BFE,
        "7": 0x0BFE,
        "8": 0x0BFE,
        "9": 0x0BFE,
        ".": 0x0B71,
        "e": 0x0B73,
        "E": 0x0B73,
        "": 0x09FF,
    },
    0x71: {
        "0": 0x0B72,
        "1": 0x0B72,
        "2": 0x0B72,
        "3": 0x0B72,
        "4": 0x0B72,
        "5": 0x0B72,
        "6": 0x0B72,
        "7": 0x0B72,
        "8": 0x0B72,
        "9": 0x0B72,
    },
    0x72: {
        "0": 0x0BFE,
        "1": 0x0BFE,
        "2": 0x0BFE,
        "3": 0x0BFE,
        "4": 0x0BFE,
        "5": 0x0BFE,
        "6": 0x0BFE,
        "7": 0x0BFE,
        "8": 0x0BFE,
        "9": 0x0BFE,
        "e": 0x0B73,
        "E": 0x0B73,
        "": 0x0AFF,
    },
    0x73: {
        "0": 0x0B75,
        "1": 0x0B75,
        "2": 0x0B75,
        "3": 0x0B75,
        "4": 0x0B75,
        "5": 0x0B75,
        "6": 0x0B75,
        "7": 0x0B75,
        "8": 0x0B75,
        "9": 0x0B75,
        "+": 0x0B74,
        "-": 0x0B74,
    },
    0x74: {
        "0": 0x0B75,
        "1": 0x0B75,
        "2": 0x0B75,
        "3": 0x0B75,
        "4": 0x0B75,
        "5": 0x0B75,
        "6": 0x0B75,
        "7": 0x0B75,
        "8": 0x0B75,
        "9": 0x0B75,
    },
    0x75: {
        "0": 0x0BFE,
        "1": 0x0BFE,
        "2": 0x0BFE,
        "3": 0x0BFE,
        "4": 0x0BFE,
        "5": 0x0BFE,
        "6": 0x0BFE,
        "7": 0x0BFE,
        "8": 0x0BFE,
        "9": 0x0BFE,
        "": 0x0AFF,
    },
    0x76: {".": 0x0B71, "e": 0x0B73, "E": 0x0B73, "": 0x09FF},
    0x78: {
        "0": 0x0B76,
        "1": 0x0B70,
        "2": 0x0B70,
        "3": 0x0B70,
        "4": 0x0B70,
        "5": 0x0B70,
        "6": 0x0B70,
        "7": 0x0B70,
        "8": 0x0B70,
        "9": 0x0B70,
    },
}

gotos = {
    0x00: 0x00,
    0x40: 0x41,
    0x42: 0x41,
    0x50: 0x51,
    0x52: 0x53,
    0x54: 0x55,
    0x56: 0x53,
    0x61: 0x60,
}

escape_characters = {"b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}

anychar = frozenset((state, table.get("", 0xFFFF)) for state, table in states.items())
groups = {}
groups[anychar] = ""
for n in range(0, 0x7F):
    catset = frozenset(
        (state, table.get(chr(n), table.get("", 0xFFFF)))
        for state, table in states.items()
    )
    if catset in groups:
        groups[catset] += chr(n)
    else:
        groups[catset] = chr(n)

catcode = [0 for n in range(0, 0x7F)]
groups.pop(anychar)
columns = [dict(anychar)]
for col, string in sorted(groups.items(), key=lambda a: a[1]):
    for ch in string:
        catcode[ord(ch)] = len(columns)
    columns.append(dict(col))

packedtable = []
mapper = dict((oldlabel, newlabel) for newlabel, oldlabel in enumerate(sorted(states)))

packedgotos = []
for newlabel, oldlabel in enumerate(sorted(states)):
    row = []
    for col in columns:
        code = col[oldlabel]
        action = code >> 8 & 0xFF
        code = code & 0xFF
        code = mapper.get(code, code)
        if code == 0xFE:
            code = newlabel
        code = action << 8 | code
        row.append(code)
    packedtable.append(row)
    goto = gotos.get(oldlabel, 255)
    packedgotos.append(mapper.get(goto, goto))

print("\n")
print("states = [")
for row in packedtable:
    print("    [", end="")
    for v in row:
        print("0x{:04x},".format(v), end="")
    print("],")
print("]")
print("gotos =", packedgotos)
print("catcode =", catcode)
