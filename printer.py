import sys, random, time
import verifier

def main():
    if len(sys.argv) < 2:
        obj = synth_json()
    else:
        with open(sys.argv[1], "r") as fd:
            obj = verifier.parse_string(fd.read().decode("utf-8"), set())
    scan = Scanner()
    stringify(scan, obj)
    scan.finish()

def synth_json(depth=0):
    if depth > 4:
        return synth_string(depth)
    return random.choice(synths)(depth)

def synth_dict(depth):
    out = {}
    for i in range(random.randint(0, 10)):
        out[synth_string(depth)] = synth_json(depth + 1)
    return out

def synth_list(depth):
    out = []
    for i in range(random.randint(0, 10)):
        out.append(synth_json(depth + 1))
    return out

def synth_const(depth):
    r = random.random()
    if r < 0.1:
        return random.choice([True, False, None])
    elif r < 0.5:
        return random.randint(0, 1000)
    elif r < 0.8:
        return synth_string(depth)
    else:
        return 1000 * (
            random.random() * random.random() - random.random() * random.random()
        )

def synth_string(depth):
    return random.choice(funny_strings)

funny_strings = [
    "progging along",
    "chug",
    "gunk",
    "hazard",
    "code",
    "bljarmer",
    "xok",
    "log",
    "blog",
    "farmer",
    "punk",
    "zebra",
    "radio",
    "epsilon",
    "gamma",
    'world "Hello" world',
    "".join(map(chr, range(40))),
    "\\",
    "".join(map(unichr, range(0x2020, 0x203F))),
    "".join(map(unichr, range(0x4020, 0x4040))),
]

synths = [synth_dict, synth_list, synth_const]

def stringify(scan, obj):
    if isinstance(obj, dict):
        scan.left()("{").blank("", 4)
        more = False
        for key, value in sorted(obj.items(), key=lambda a: a[0]):
            if more:
                scan(",").blank(" ", 4)
            scan.left()
            scan(escape_string(key) + ": ")
            stringify(scan, value)
            scan.right()
            more = True
        scan.blank("", 0)("}").right()
    elif isinstance(obj, list):
        scan.left()("[").blank("", 4)
        more = False
        for item in obj:
            if more:
                scan(",").blank(" ", 4)
            stringify(scan, item)
            more = True
        scan.blank("", 0)("]").right()
    elif isinstance(obj, (str, unicode)):
        scan(escape_string(obj))
    elif obj is None:
        scan("null")
    elif obj == True:
        scan("true")
    elif obj == False:
        scan("false")
    elif isinstance(obj, (int, long, float)):  
        scan(str(obj))  
    else:
        assert False, "no handler: " + repr(obj)

def escape_string(string):
    out = ['"']
    for ch in string:
        n = ord(ch)
        if (
            0x20 <= n and n <= 0x7E or 0xFF < n
        ):  
            if ch == "\\":  
                ch = "\\\\"
            elif ch == '"':
                ch = '\\"'
        else:
            a = "0123456789abcdef"[n >> 12]
            b = "0123456789abcdef"[n >> 8 & 15]
            c = "0123456789abcdef"[n >> 4 & 15]
            d = "0123456789abcdef"[n & 15]
            ch = "u" + a + b + c + d
            ch = "\\" + character_escapes.get(n, ch)
        out.append(ch)
    out.append('"')
    return "".join(out)

character_escapes = {8: "b", 9: "t", 10: "n", 12: "f", 13: "r"}

class Scanner(object):
    def __init__(self):
        self.printer = Printer()
        self.stream = []
        self.stack = []
        self.lastblank = None
        self.left_total = 1
        self.right_total = 1  

    def left(self):
        return self(Left())

    def right(self):
        return self(Right())

    def blank(self, text, indent=0):
        return self(Blank(text, indent))

    def __call__(self, x):
        if isinstance(x, Left):
            x.size = -self.right_total
            self.stack.append(x)
        elif isinstance(x, Right):
            if len(self.stack) > 0:
                self.stack.pop().size += self.right_total
        elif isinstance(x, Blank):
            if self.lastblank is not None:
                self.lastblank.size += self.right_total
            self.lastblank = x
            x.size = -self.right_total
            self.right_total += len(x.text)
        else:
            self.right_total += len(x)
        self.stream.append(x)
        while (
            len(self.stream) > 0
            and self.right_total - self.left_total > 3 * self.printer.margin
        ):
            self.left_total += self.printer(self.stream.pop(0))
        return self

    def finish(self):
        if self.lastblank is not None:  
            self.lastblank.size += self.right_total  
        while len(self.stream) > 0:
            self.printer(self.stream.pop(0))
        sys.stdout.write("\n")

class Printer(object):
    def __init__(self):
        self.margin = 80
        self.layout = Layout(None, 80, False)
        self.spaceleft = 80
        self.spaces = 80

    def __call__(self, x):
        if isinstance(x, Left):
            self.layout = Layout(
                self.layout, self.spaces, x.size < 0 or self.spaceleft < x.size
            )
            return 0
        elif isinstance(x, Right):
            if self.layout.parent:
                self.layout = self.layout.parent
            return 0
        elif isinstance(x, Blank):
            if x.size < 0 or self.spaceleft < x.size or self.layout.force_break:
                self.spaces = self.layout.spaces - x.indent
                self.spaceleft = self.spaces
                sys.stdout.write("\n" + " " * (self.margin - self.spaces))
            else:
                sys.stdout.write(x.text.encode("utf-8"))
                self.spaceleft -= len(x.text)
            return len(x.text)
        else:
            sys.stdout.write(x.encode("utf-8"))
            self.spaceleft -= len(x)
            return len(x)

class Layout(object):
    def __init__(self, parent, spaces, force_break):
        self.parent = parent
        self.spaces = spaces
        self.force_break = force_break

class Left(object):
    def __init__(self):
        self.size = 0

class Right(object):
    pass

class Blank(object):
    def __init__(self, text, indent=0):
        self.text = text
        self.indent = indent
        self.size = 0

if __name__ == "__main__":
    main()