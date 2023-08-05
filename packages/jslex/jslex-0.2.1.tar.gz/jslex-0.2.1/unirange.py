import unicodedata

ranges = {}

classes = {
    'letters': "Lu Ll Lt Lm Lo Nl",
    'combining': "Mn Mc",
    'digit': "Nd",
    'connector': "Pc",
    }

cat_to_class = {}
ranges = {}

for klass, cats in classes.items():
    for cat in cats.split():
        cat_to_class[cat] = klass
    ranges[klass] = []

for i in range(0xFFFF):
    cat = unicodedata.category(unichr(i))
    try:
        klass = cat_to_class[cat]
    except KeyError:
        continue
    r = ranges[klass]
    if r and r[-1][1] == i-1:
        r[-1][1] = i
    else:
        r.append([i, i])

for k, r in ranges.items():
    reg = "["
    for a,b in r:
        if a == b:
            reg += r"\u%04x" % a
        else:
            reg += r"\u%04x-\u%04x" % (a, b)
    reg += "]"
    print "%s = %s" % (k, reg)

